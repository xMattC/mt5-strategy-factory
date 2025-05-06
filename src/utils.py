import configparser
import logging
import shutil
from datetime import datetime
from pathlib import Path

from src.log_config import setup_logging
from src.path_config import load_paths

logger = logging.getLogger(__name__)


def copy_mt5_report(ini_path: Path, dest_dir: Path):
    """ Copies the MT5-generated report (defined in an .ini file) from the MT5 reports folder to a destination folder.

    param ini_path: Path to the .ini file used in the run
    param dest_dir: Path to copy the report to (your local results folder)
    """
    config = configparser.ConfigParser()
    config.optionxform = str  # Preserve case
    config.read(ini_path, encoding="utf-16")

    paths = load_paths()
    report_name = config["Tester"]["Report"]
    src_file = paths["MT5_ROOT"] / f"{report_name}.xml"
    dest_file = dest_dir / f"{report_name}.xml"

    if not src_file.exists():
        logger.error(f"Report not found: {src_file}")
        raise FileNotFoundError(f"Report not found: {src_file}")

    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(src_file, dest_file)
    logger.info(f"Copied MT5 report '{report_name}.htm' to: {dest_file}")


def delete_mt5_test_cache():
    """ Deletes all files in the MetaTrader 5 Tester\\cache directory.

    param test_cache_dir: Path to the Tester\\cache directory
    """
    paths = load_paths()
    test_cache_dir = paths["MT5_TEST_CACHE"]
    if test_cache_dir.exists() and test_cache_dir.is_dir():
        deleted = 0
        for file in test_cache_dir.iterdir():
            if file.is_file():
                file.unlink()
                deleted += 1
        logger.info(f"Cleared {deleted} file(s) from MT5 test cache at: {test_cache_dir}")
    else:
        logger.warning(f"MT5 test cache directory does not exist: {test_cache_dir}")


def create_dir_structure(run_name: str, indicator_type: str) -> Path:
    """ Create a standardized directory structure for a given run and return the base path.

    param run_name: Name of the run (e.g., zuse, test1)
    param indicator_type: Indicator type folder (e.g., C1, Volume)
    return: Path to the run's base output directory
    """
    paths = load_paths()
    base_path = paths["PRO_ROOT"]
    indi_path = base_path / "Outputs" / run_name / indicator_type

    (indi_path / "experts").mkdir(parents=True, exist_ok=True)
    (indi_path / "ini_files").mkdir(parents=True, exist_ok=True)
    (indi_path / "results").mkdir(parents=True, exist_ok=True)

    logger.info(f"Created directory structure under: {indi_path}")
    return indi_path


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
