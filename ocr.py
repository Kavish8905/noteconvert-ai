from __future__ import annotations
import base64
from pathlib import Path
import httpx
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
from app.config import settings

def preprocess_image(input_path: Path) -> Path:
    image = Image.open(input_path).convert("RGB")
    image.thumbnail((2200, 2200))
    image = ImageOps.exif_transpose(image)
    gray = ImageOps.grayscale(image)
    gray = ImageEnhance.Contrast(gray).enhance(1.25)
    out = input_path.with_name(f"{input_path.stem}_prep.jpg")
    gray.save(out, "JPEG", quality=92, optimize=True)
    return out

async def gemini_transcribe(image_path: Path) -> str:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    data = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    prompt = """Transcribe the document image exactly and cleanly.
Requirements:
- Preserve headings and lists where possible.
- Support Hindi and English.
- Do not invent missing text.
- If a word is genuinely unreadable, write [unclear] instead of guessing.
Return only the transcription."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
    )
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": data}},
            ]
        }]
    }
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        body = response.json()
    try:
        return body["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as exc:
        raise RuntimeError("Gemini returned no transcription") from exc

def tesseract_transcribe(image_path: Path) -> str:
    # English + Hindi if the corresponding traineddata is installed.
    lang = "eng+hin"
    try:
        return pytesseract.image_to_string(Image.open(image_path), lang=lang).strip()
    except pytesseract.TesseractError:
        return pytesseract.image_to_string(Image.open(image_path), lang="eng").strip()

async def transcribe(image_path: Path) -> str:
    prepared = preprocess_image(image_path)
    try:
        if settings.ocr_provider.lower() == "tesseract":
            return tesseract_transcribe(prepared)
        return await gemini_transcribe(prepared)
    finally:
        if prepared.exists() and prepared != image_path:
            prepared.unlink(missing_ok=True)
