"""LLM client factory - returns the correct client based on config."""

from app.core.interfaces import LLMClient
from app.infrastructure.llm.ollama_client import OllamaClient
from app.utils.config import config
from app.utils.logger import logger


def get_llm_client() -> LLMClient:
    """Factory function that returns the configured LLM client."""
    provider = config.LLM_PROVIDER.lower()

    if provider == "ollama":
        logger.info("Using Ollama LLM client")
        return OllamaClient()

    logger.warning(f"Unknown LLM provider '{provider}', falling back to Ollama")
    return OllamaClient()
