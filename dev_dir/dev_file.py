from subprocess import run, CalledProcessError
from time import perf_counter
from pathlib import Path

# Path to the MetaTrader 5 terminal executable
MT5_TERM_EXE = Path(r'C:\Program Files\FTMO MetaTrader 5\terminal64.exe')

# Path to the .ini configuration file for the test
INI_FILE = Path(
    r'C:\Users\mkcor\AppData\Roaming\MetaQuotes\Terminal\49CDDEAA95A409ED22BD2287BB67CB9C\MQL5\Experts\meta-strategist\dev_dir\Aroon.ini'
)
TEST_CASH = Path.joinpath(MT5_TERM_EXE, r"Tester\cache")


def run_test(ini_file: Path):
    """Launches MetaTrader 5 with a .ini configuration file.

    param ini_file: Path to the .ini file used for testing or optimization.
    """
    start = perf_counter()  # Start high-precision timer

    try:
        run([str(MT5_TERM_EXE), f'/config:{ini_file}'], check=True)
        print(f"[INFO] MT5 ran successfully in {perf_counter() - start:.2f}s.")

    except CalledProcessError as e:
        print(f"[ERROR] MT5 failed after {perf_counter() - start:.2f}s. Code: {e.returncode}")
        raise


def delete_mt5_test_cache(test_cash):
    """ Deletes all files in the MetaTrader 5 Tester\\cache directory."""
    if test_cash.exists() and test_cash.is_dir():
        for file in test_cash.iterdir():
            if file.is_file():
                file.unlink()


if __name__ == "__main__":
    run_test(INI_FILE)
