import shutil
import subprocess
from pathlib import Path


def run_mt5_test(mt5_terminal_path: Path, config_path: Path):
    """
    Executes MetaTrader 5 in command-line mode with a given config.

    Parameters:
    mt5_terminal_path: Path to terminal64.exe
    config_path: Path to the .ini configuration file
    """
    cmd = f'"{mt5_terminal_path}" /config:"{config_path}"'
    subprocess.call(cmd, shell=True)


def copy_report_file(mt5_root: Path, report_name: str, destination: Path):
    """
    Copies the generated XML report file from MT5 root to a destination folder.

    Parameters:
    mt5_root: Root MT5 directory
    report_name: Name of the report without extension
    destination: Directory to copy the XML to
    """
    src = mt5_root / f"{report_name}.xml"
    dst = destination / f"{report_name}.xml"
    if src.exists():
        shutil.copy(src, dst)
    else:
        print(f"Warning: Report file {src} not found.")
