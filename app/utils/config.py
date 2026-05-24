"""Configuration management using environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()


class Config:
    """Centralized configuration."""

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    DATABASE_PATH: Path = Path(os.getenv("DATABASE_PATH", "data/kb.db"))

    PDF_PATH: Path = Path(os.getenv("PDF_PATH", "data/SLATEFALL_DOSSIER.pdf"))

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


config = Config()
