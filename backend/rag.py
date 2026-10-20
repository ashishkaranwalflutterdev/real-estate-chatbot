import json
import math
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

DATA_PATH = Path(__file__).resolve().parent / "data" / "knowledge_base.json"


class Retriever:
    def __init__(self, data_file: Path = DATA_PATH):
        self.data_file = data_file
        self.docs: List[Dict[str, Any]] = []
        self.tokens: List[List[str]] = []
        self.idf: Dict[str, float] = {}
        self.k1 = 1.5
        self.b = 0.75
        self.build_index()

    def tokenize(self, text: str) -> List[str]:
        # Lowercase and split on punctuation / whitespace
        return re.findall(r"\b[a-zA-Z0-9_\-\$]+\b", text.lower())

    def build_index(self):
        if not self.data_file.exists():
            return

        with open(self.data_file, "r", encoding="utf-8") as f:
            self.docs = json.load(f)

        self.tokens = []
        df: Dict[str, int] = {}
        total = len(self.docs)

        for item in self.docs:
            merged = f"{item.get('title', '')} {item.get('category', '')} {item.get('source', '')} {item.get('content', '')}"
            toks = self.tokenize(merged)
            self.tokens.append(toks)

            for t in set(toks):
                df[t] = df.get(t, 0) + 1

        self.idf = {
            t: math.log((total - count + 0.5) / (count + 0.5) + 1.0)
            for t, count in df.items()
        }

    def search(self, query: str, limit: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        if not self.docs:
            return []

        q_terms = self.tokenize(query)
        if not q_terms:
            return [(d, 1.0) for d in self.docs[:limit]]

        avg_dl = sum(len(t) for t in self.tokens) / max(len(self.tokens), 1)
        results: List[Tuple[Dict[str, Any], float]] = []

        q_lower = query.lower()

        for idx, (doc, toks) in enumerate(zip(self.docs, self.tokens)):
            score = 0.0
            doc_len = len(toks)
            counts: Dict[str, int] = {}
            for t in toks:
                counts[t] = counts.get(t, 0) + 1

            for term in q_terms:
                if term in counts:
                    tf = counts[term]
                    idf = self.idf.get(term, 0.5)
                    num = tf * (self.k1 + 1)
                    denom = tf + self.k1 * (1 - self.b + self.b * (doc_len / avg_dl))
                    term_score = idf * (num / denom)

                    # Boost matches appearing directly in the title
                    if term in self.tokenize(doc.get("title", "")):
                        term_score *= 2.0

                    score += term_score

            # Boost exact substring matches in title or source
            if doc.get("title", "").lower() in q_lower:
                score += 5.0
            if doc.get("source", "").lower() in q_lower:
                score += 1.5

            if score > 0.1:
                results.append((doc, round(score, 3)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def make_grounded_prompt(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        ctx_blocks = []
        for i, item in enumerate(context_chunks, 1):
            ctx_blocks.append(
                f"[{i}] {item.get('title')} ({item.get('source')})\n"
                f"URL: {item.get('url')}\n"
                f"Category: {item.get('category')}\n"
                f"{item.get('content')}"
            )

        context_text = "\n\n".join(ctx_blocks)

        prompt = (
            "You are a helpful real estate assistant representing Dar Global (London-listed luxury real estate) "
            "and Wasalt (Saudi Arabia's leading PropTech marketplace).\n\n"
            "Grounding Rules:\n"
            "1. Answer strictly based on the Context below.\n"
            "2. If the question cannot be answered from the Context, politely state that official public info is not available.\n"
            "3. Cite your sources clearly at the end with the title and URL.\n"
            "4. Keep the tone professional, concise, and helpful.\n\n"
            f"Context:\n{context_text}\n\n"
            f"User Question: {query}\n\n"
            "Response:"
        )
        return prompt


# Shared retriever instance
retriever = Retriever()
