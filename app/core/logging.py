
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "storage" / "logs"
LOG_FILE = LOG_DIR / "bizpilot.log"


def setup_logging() -> None:
    """Configure application-wide logging."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_level = getattr(logging, settings.log_level)

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    # Avoid duplicate handlers if setup is called again.
    root_logger.handlers.clear()

    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named application logger."""

    return logging.getLogger(name)
