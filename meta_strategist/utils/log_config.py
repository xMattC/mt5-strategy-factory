import logging
from pathlib import Path


def setup_logging(log_file: Path = None, level: int = logging.INFO):
    """
    Configure logging globally. Writes to console and optionally to a log file.

    param log_file: Optional path to a log file
    param level: Logging level (e.g., logging.INFO, logging.DEBUG)
    """
    log_format = "%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
    handlers = [logging.StreamHandler()]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )
