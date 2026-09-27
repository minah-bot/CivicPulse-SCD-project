import os
from functools import lru_cache
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    redis_url: str
    triage_provider: str
    rate_limit_per_minute: int
    cache_ttl_seconds: int
    triage_cache_ttl_hours: int
    groq_api_key: str
    gemini_api_key: str
    ollama_base_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.environ.get(
            "DATABASE_URL", "postgresql+psycopg://civicpulse:civicpulse@localhost:5432/civicpulse"
        ),
        redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        triage_provider=os.environ.get("TRIAGE_PROVIDER", "simulated"),
        rate_limit_per_minute=int(os.environ.get("RATE_LIMIT_PER_MINUTE", "30")),
        cache_ttl_seconds=int(os.environ.get("CACHE_TTL_SECONDS", "30")),
        triage_cache_ttl_hours=int(os.environ.get("TRIAGE_CACHE_TTL_HOURS", "24")),
        groq_api_key=os.environ.get("GROQ_API_KEY", ""),
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434"),
    )
