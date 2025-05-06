import logging
from datetime import datetime
from pathlib import Path

from meta_strategist.utils.log_config import setup_logging


def init_stage_logger(stage_name: str, output_base: Path) -> logging.Logger:
    """ Set up logging to a stage-specific log file under the given output path.

    param stage_name: Name of the pipeline stage (e.g. 'C1', 'Volume')
    param output_base: The stage's base output directory (where /logs will be created)
    return: Configured logger for the stage
    """
    log_dir = output_base / "logs"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    log_file = log_dir / f"{stage_name}_{timestamp}.log"

    setup_logging(log_file)
    logger = logging.getLogger(stage_name)
    logger.info(f"Logging initialized for stage: {stage_name} optimisation")
    return logger
