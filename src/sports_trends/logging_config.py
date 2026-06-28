"""Logging helpers for sports-trends jobs."""

from __future__ import annotations

import logging
import os

_CONFIGURED = False


def configure_logging(level: int | None = None) -> None:
    """Configure root logging once, honouring ``SPORTS_LOG_LEVEL``."""
    global _CONFIGURED
    if _CONFIGURED:
        return
    if level is None:
        level = getattr(logging, os.getenv("SPORTS_LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for ``name`` (e.g. ``__name__``)."""
    configure_logging()
    return logging.getLogger(name)
