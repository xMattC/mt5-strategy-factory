import logging
from datetime import datetime
from pathlib import Path


def setup_logging(log_file: Path = None, level: int = logging.INFO):
    """
    Configure global logging. Logs to console, and optionally to a file.

    param log_file: Optional path to a log file
    param level: Logging level (e.g., logging.INFO, logging.DEBUG)
    """
    log_format = "%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
    formatter = logging.Formatter(log_format)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers to avoid duplication
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    # Always add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Optionally add file handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def init_stage_logger(stage_name: str, output_base: Path) -> logging.Logger:
    """
    Set up logging for a specific optimization stage (e.g., 'C1').

    param stage_name: Name of the pipeline stage
    param output_base: Path to the stage's output directory
    return: Stage-specific logger instance
    """
    log_dir = output_base / "logs"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    log_file = log_dir / f"{stage_name}_{timestamp}.log"

    setup_logging(log_file)
    logger = logging.getLogger(stage_name)
    logger.info(f"Logging initialized for stage: {stage_name} optimisation")
    return logger
