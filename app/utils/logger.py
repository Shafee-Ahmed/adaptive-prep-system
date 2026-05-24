"""Logging configuration."""

import logging
import sys

from app.utils.config import config


def setup_logger() -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger("adaptive_prep")
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)
    
    return logger


# Singleton logger instance
logger = setup_logger()