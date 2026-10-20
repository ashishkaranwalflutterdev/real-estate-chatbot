import os
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger("openrouter")

API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Prioritized list of active free models on OpenRouter
MODELS = [
    "nvidia/nemotron-3.5-lightning:free",
    "google/gemma-4-26b-a4b-it:free",
    "minimax/minimax-m3.1-flash:free",
    "liquid/lfm-2.5-2.6b:free",
]


class OpenRouterService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")

    def complete(self, prompt: str, system: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "answer": "OpenRouter API key is not set. Please add OPENROUTER_API_KEY to your backend/.env file.",
                "model_used": "none",
                "status": "error",
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ashishkaranwalflutterdev/real-estate-chatbot",
            "X-Title": "DarGlobal & Wasalt Real Estate Bot",
        }

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        last_error = ""

        # Try models in order; fall back if upstream is busy or rate-limited
        for model_id in MODELS:
            payload = {
                "model": model_id,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 750,
            }

            try:
                res = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=25)
                data = res.json()

                if res.status_code == 200 and data.get("choices"):
                    msg = data["choices"][0].get("message", {}) or {}
                    raw = msg.get("content") or msg.get("reasoning") or ""
                    text = str(raw).strip()

                    # Strip reasoning tags if model emitted thought tokens
                    if "<think>" in text and "</think>" in text:
                        text = text.split("</think>")[-1].strip()

                    if not text:
                        continue

                    return {
                        "answer": text,
                        "model_used": data.get("model", model_id),
                        "status": "success",
                    }
                else:
                    err = data.get("error", {}).get("message", res.text)
                    logger.warning(f"Model {model_id} returned {res.status_code}: {err}")
                    last_error = f"{model_id}: {err}"

            except Exception as e:
                logger.warning(f"Failed request to {model_id}: {e}")
                last_error = f"{model_id}: {e}"

        return {
            "answer": f"Unable to reach free model providers at this moment. ({last_error})",
            "model_used": "exhausted",
            "status": "error",
        }
