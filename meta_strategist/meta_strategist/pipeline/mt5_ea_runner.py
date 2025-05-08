import logging
from subprocess import run, CalledProcessError
from time import perf_counter
from pathlib import Path

from meta_strategist.utils.pathing import load_paths

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

    try:
        logger.info(f"Running MT5 with INI: {ini_file}")
        run([mt5_terminal, f'/config:{ini_file}'], check=True)
        logger.info(f"MT5 ran successfully ({ini_file.name}) in {perf_counter() - start:.2f}s")

    except CalledProcessError as e:
        logger.error(f"MT5 failed ({ini_file.name}) after {perf_counter() - start:.2f}s "
                     f"with return code {e.returncode}")
        raise
