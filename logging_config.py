"""Logging configuration for the Clockodo MCP server."""

from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_FILE = LOG_DIR / "clockodo.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
MAX_LOG_BYTES = 1_000_000
BACKUP_COUNT = 3


def setup_logging(level: int = logging.INFO) -> None:
    """Configure application-wide logging with a rotating file handler."""
    if logging.getLogger().handlers:
        return

    LOG_DIR.mkdir(exist_ok=True)

    handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_BYTES, backupCount=BACKUP_COUNT)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
