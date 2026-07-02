from __future__ import annotations

import logging
import sys
from pathlib import Path

from config.settings import get_settings


def configure_logging(log_level: str | None = None, log_dir: str | None = None) -> logging.Logger:
    """Configure application logging for console and file output."""
    settings = get_settings(validate_required=False)
    resolved_level = (log_level or settings.log_level).upper()
    resolved_dir = log_dir or settings.log_dir

    log_path = Path(resolved_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("blackcrest")
    logger.setLevel(getattr(logging, resolved_level, logging.INFO))
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False

    return logger
