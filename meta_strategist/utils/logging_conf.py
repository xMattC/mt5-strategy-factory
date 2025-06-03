from datetime import datetime
from pathlib import Path

import sys
import logging


def setup_logging(log_file: Path = None, level: int = logging.INFO):
    log_format = "%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
    formatter = logging.Formatter(log_format)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear old handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler to stdout (not stderr)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Optional file logging
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


import logging
from pathlib import Path
from datetime import datetime

def init_stage_logger(stage_name: str, output_base: Path) -> logging.Logger:
    """
    Set up logging for a specific optimisation stage (e.g., 'C1').

    param stage_name: Name of the pipeline stage
    param output_base: Path to the stage's output directory
    return: Stage-specific logger instance
    """
    log_dir = output_base / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)  # Ensure log directory exists

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    log_file = log_dir / f"{stage_name}_{timestamp}.log"

    logger = logging.getLogger(stage_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent duplicate logs if root logger is configured

    # Remove all handlers if already attached (prevents duplicates on re-run)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter for PyCharm: filename:lineno: LEVEL: message
    formatter = logging.Formatter("%(filename)s:%(lineno)d: %(levelname)s: %(message)s")

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler (optional, but useful for immediate feedback)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info(f"Logging initialized for stage: {stage_name}")
    return logger

