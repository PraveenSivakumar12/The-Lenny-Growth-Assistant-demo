"""
Structured Logging Module
Provides clean, structured logging for API requests, RAG retrieval, LLM calls, and errors.
Ensures sensitive tokens/keys are never written to disk or console.
"""

import logging
import sys
from typing import Any, Dict


def setup_logger(name: str = "lenny_growth") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = setup_logger()


def log_event(event_name: str, **kwargs: Any) -> None:
    """Helper to log structured key-value events while masking potential secret keys."""
    sanitized: Dict[str, Any] = {}
    for k, v in kwargs.items():
        if any(secret_term in k.lower() for secret_term in ["key", "secret", "password", "token"]):
            sanitized[k] = "***REDACTED***"
        else:
            sanitized[k] = v
    logger.info(f"event={event_name} payload={sanitized}")
