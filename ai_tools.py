from __future__ import annotations
import httpx
from app.config import settings

async def generate_from_text(text: str, operation: str) -> str:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    prompts = {
        "summary": "Create concise study notes from this source. Do not add facts not present in the source.",
        "mcqs": "Create 10 MCQs from this source. Give 4 options and mark the correct answer. Use only information from the source.",
        "flashcards": "Create 10 study flashcards from this source in Q/A format. Use only information from the source.",
        "clean_notes": "Clean and structure this OCR text into readable study notes. Preserve meaning. Do not add facts.",
    }
    instruction = prompts.get(operation)
    if not instruction:
        raise ValueError(f"Unsupported operation: {operation}")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
    )
    payload = {
        "contents": [{
            "parts": [{"text": f"{instruction}\n\nSOURCE:\n{text}"}]
        }]
    }
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        body = response.json()
    return body["candidates"][0]["content"]["parts"][0]["text"].strip()
