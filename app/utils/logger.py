"""Logging configuration."""

import logging
import sys

from app.utils.config import config


def setup_logger() -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger("adaptive_prep")
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)

    return logger


logger = setup_logger()
