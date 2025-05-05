from subprocess import run, CalledProcessError
from time import perf_counter
from pathlib import Path
from src.path_config import load_paths


def run_ea(ini_file: Path):
    """ Run a MetaTrader 5 instance using a specified .ini configuration file.

    param mt5_terminal: Path to MetaTrader 5 terminal executable
    param ini_file: Path to the .ini configuration file to run
    """
    start = perf_counter()
    paths = load_paths()
    mt5_terminal = str(paths["MT5_TERM_EXE"])

    try:
        # Run MT5 terminal with given ini file; must complete successfully
        run([mt5_terminal, f'/config:{ini_file}'], check=True)
        print(f"[INFO] MT5 ran successfully in {perf_counter() - start:.2f}s.")

    except CalledProcessError as e:
        # If MT5 execution fails, log error and re-raise exception
        print(f"[ERROR] MT5 failed after {perf_counter() - start:.2f}s. Code: {e.returncode}")
        raise


def run_all_eas(ini_dir: Path):
    """ Run all Expert Advisors by executing each .ini configuration file found in the given directory.

    param mt5_terminal: Path to MetaTrader 5 terminal executable
    param ini_dir: Directory containing .ini configuration files
    """

    for ini_file in ini_dir.glob("*.ini"):  # Iterate over all .ini files and run each EA individually
        print("ini_dir: ", ini_dir)
        run_ea(ini_file)
