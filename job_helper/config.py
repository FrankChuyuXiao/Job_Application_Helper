from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str
    database_path: str


def load_settings() -> Settings:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-5.2").strip()
    database_path = os.getenv("DATABASE_PATH", "data/jobs.db").strip()

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Create a .env file from .env.example and add your key."
        )

    return Settings(
        openai_api_key=api_key,
        openai_model=model,
        database_path=database_path,
    )
