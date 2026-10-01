from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str
    gemini_api_key: str | None
    gemini_model: str
    ocr_provider: str
    free_credits: int
    referral_reward: int
    max_file_mb: int
    session_ttl_minutes: int
    admin_ids: tuple[int, ...]

def _int_tuple(value: str) -> tuple[int, ...]:
    if not value.strip():
        return ()
    return tuple(int(x.strip()) for x in value.split(",") if x.strip())

settings = Settings(
    bot_token=os.environ["BOT_TOKEN"],
    database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./noteconvert.db"),
    gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
    gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
    ocr_provider=os.getenv("OCR_PROVIDER", "gemini"),
    free_credits=int(os.getenv("FREE_CREDITS", "20")),
    referral_reward=int(os.getenv("REFERRAL_REWARD", "5")),
    max_file_mb=int(os.getenv("MAX_FILE_MB", "20")),
    session_ttl_minutes=int(os.getenv("SESSION_TTL_MINUTES", "60")),
    admin_ids=_int_tuple(os.getenv("ADMIN_IDS", "")),
)
