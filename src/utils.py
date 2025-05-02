from subprocess import run, CalledProcessError
from time import perf_counter
from pathlib import Path


def delete_mt5_test_cache(test_cache_dir: Path):
    """Deletes all files in the MetaTrader 5 Tester\\cache directory.

    param test_cache_dir: Path to the Tester\\cache directory
    """
    if test_cache_dir.exists() and test_cache_dir.is_dir():
        for file in test_cache_dir.iterdir():
            if file.is_file():
                file.unlink()
        print(f"[INFO] Cleared MT5 test cache at: {test_cache_dir}")


def create_structure(base_path: Path, run_name: str, indicator_type: str) -> None:
    """Create a standardized directory structure for a given run.

    param base_path: Root path for the project
    param run_name: Name of the run (e.g., zuse, test1)
    param indicator_type: Indicator type folder (e.g., C1, Volume)
    """
    indi_path = base_path / "Outputs" / run_name / indicator_type
    (indi_path / "experts").mkdir(parents=True, exist_ok=True)
    (indi_path / "ini_files").mkdir(parents=True, exist_ok=True)
    (indi_path / "results").mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Created directory structure under: {indi_path}")
