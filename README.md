# Real Estate AI Chatbot (Dar Global & Wasalt)

A grounded AI chatbot designed to answer inquiries using public information from **Dar Global** ([darglobal.co.uk](https://darglobal.co.uk/)) and **Wasalt** ([wasalt.sa](https://wasalt.sa/en)).

Built with **Next.js 14**, **FastAPI (Python)**, and **OpenRouter free models**.

---

## Architecture Overview

I structured the project as a single container application:
* **Frontend**: Next.js 14 (React, TypeScript) configured for static export (`output: 'export'`). It features a dark/gold theme matching Dar Global's branding, with quick prompt chips and linked source citations.
* **Backend**: FastAPI serving REST endpoints (`/api/chat`, `/api/health`, `/api/stats`) and directly mounting the exported Next.js frontend at `/`.
* **RAG Pipeline**: A custom BM25 keyword-relevance retriever indexing verified public data from Dar Global projects and Wasalt's PropTech platform.
* **Model Layer**: Connects to OpenRouter's free tier (`nvidia/nemotron-3.5-lightning:free` with automatic fallback to `google/gemma-4-26b-a4b-it:free` and `minimax/minimax-m3.1-flash:free` if an upstream provider hits rate limits).

---

## Local Setup

### 1. Requirements
* Python 3.9+
* Node.js 18+ (tested on Node 20/22)
* OpenRouter API key ([openrouter.ai](https://openrouter.ai))

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/ashishkaranwalflutterdev/real-estate-chatbot.git
cd real-estate-chatbot

# Create virtualenv and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Add your OpenRouter API key
cp .env.example backend/.env
# Put OPENROUTER_API_KEY=your_key in backend/.env

# Run FastAPI server
uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend Development (Optional)
If modifying the frontend:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000`. It proxies queries directly to `http://localhost:8000`.

To produce a production build for FastAPI:
```bash
cd frontend
npm run build
```

---

## Running with Docker

I created a multi-stage Dockerfile that builds the Next.js static files and runs the lightweight Python container:

```bash
# Build and run with Docker Compose
docker-compose up --build
```
The full app will be live at `http://localhost:8000`.

---

## Verification & Testing

```bash
# Verify the ethical ingestion script & robots.txt permissions
python backend/data/scraper.py

# Test RAG retrieval logic directly
python -c "
from backend.rag import retriever
hits = retriever.search('AIDA in Oman')
for doc, score in hits:
    print(f'[{score}] {doc[\"title\"]} ({doc[\"source\"]})')
"
```

---

## Author
* **Ashish** — `flutterdevak@gmail.com`
* GitHub: [ashishkaranwalflutterdev](https://github.com/ashishkaranwalflutterdev)
