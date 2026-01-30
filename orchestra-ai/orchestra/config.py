from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    model: str
    mock_mode: bool
    cache_dir: str
    data_dir: str

def load_settings() -> Settings:
    load_dotenv()
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    mock_mode = os.getenv("MOCK_MODE", "true").lower() == "true"
    cache_dir = os.getenv("CACHE_DIR", ".cache")
    data_dir = os.getenv("DATA_DIR", "data")
    return Settings(model=model, mock_mode=mock_mode, cache_dir=cache_dir, data_dir=data_dir)
