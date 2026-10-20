import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .openrouter import OpenRouterService
from .rag import retriever

# Load environment variables from backend/.env or root .env
ENV_PATH = Path(__file__).resolve().parent / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY", "")

app = FastAPI(
    title="Real Estate Chatbot API",
    description="Grounded AI assistant for Dar Global and Wasalt",
    version="1.0.0",
)

# CORS setup for local Next.js dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_client = OpenRouterService(api_key=API_KEY)


class MessagePayload(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []


class SourceCitation(BaseModel):
    title: str
    source: str
    url: str
    category: str


class ChatResult(BaseModel):
    reply: str
    citations: List[SourceCitation]
    model_used: str
    status: str


@app.get("/api/health")
def get_health():
    return {
        "status": "healthy",
        "indexed_docs": len(retriever.docs),
        "has_key": bool(ai_client.api_key),
    }


@app.get("/api/stats")
def get_stats():
    return {
        "total_documents": len(retriever.docs),
        "sources": list({d.get("source") for d in retriever.docs}),
        "sample_prompts": [
            "What is AIDA in Oman and which brand partners are involved?",
            "What services and property types are offered on Wasalt?",
            "Tell me about Dar Global's partnership with Automobili Lamborghini and Pagani.",
            "How does Wasalt ensure compliance with Saudi REGA Fal broker licensing?",
            "What are Dar Global's latest financial results and GDV?",
        ],
    }


@app.post("/api/chat", response_model=ChatResult)
def handle_chat(payload: MessagePayload):
    text = payload.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Retrieve relevant context
    hits = retriever.search(text, limit=3)
    chunks = [doc for doc, _ in hits]

    citations = [
        SourceCitation(
            title=d.get("title", ""),
            source=d.get("source", ""),
            url=d.get("url", ""),
            category=d.get("category", ""),
        )
        for d in chunks
    ]

    # Build prompt and call model
    prompt = retriever.make_grounded_prompt(text, chunks)
    res = ai_client.complete(prompt)

    return ChatResult(
        reply=res["answer"],
        citations=citations,
        model_used=res["model_used"],
        status=res["status"],
    )


# Serve Next.js exported static assets in production container
BUILD_DIR = Path(__file__).resolve().parent.parent / "frontend" / "out"
if BUILD_DIR.exists():
    app.mount("/", StaticFiles(directory=str(BUILD_DIR), html=True), name="static_frontend")
