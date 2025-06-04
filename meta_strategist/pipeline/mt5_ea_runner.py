import logging
from subprocess import run, CalledProcessError
from time import perf_counter
from pathlib import Path
import psutil
import sys

from meta_strategist.utils import load_paths

logger = logging.getLogger(__name__)


def run_ea(ini_file: Path):
    """ Run a MetaTrader 5 instance using a specified .ini configuration file.

    param ini_file: Path to the .ini configuration file to run
    """
    start = perf_counter()
    paths = load_paths()
    mt5_terminal = str(paths["MT5_TERM_EXE"])

    if not ini_file:
        logger.warning(f"No .ini files {ini_file} found")
        return

    if is_mt5_running(mt5_terminal):
        logger.error("MetaTrader 5 terminal is already running! Please close it before running automation.")
        sys.exit(1)  # Exit with error code

    try:
        logger.info(f"Running MT5 with INI: {ini_file}")
        run([mt5_terminal, f'/config:{ini_file}'], check=True)
        logger.info(f"MT5 ran successfully ({ini_file.name}) in {perf_counter() - start:.2f}s")

    except CalledProcessError as e:
        logger.error(f"MT5 failed ({ini_file.name}) after {perf_counter() - start:.2f}s "
                     f"with return code {e.returncode}")
        raise


def is_mt5_running(mt5_path: str) -> bool:
    """Return True if a MetaTrader 5 terminal is running matching the given executable path."""
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['exe'] and Path(proc.info['exe']) == Path(mt5_path):
                return True
        except Exception:
            pass
    return False
