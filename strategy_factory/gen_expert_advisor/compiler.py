import subprocess
from pathlib import Path
from strategy_factory.utils import load_paths
import logging

logger = logging.getLogger(__name__)


def compile_ea(ea_mq5_path: Path) -> None:
    """ Compile a .mq5 file to .ex5 using MetaEditor as a subprocess.

    param ea_mq5_path: Path to the .mq5 file to compile
    """
    # Check that the .mq5 source file exists
    if not ea_mq5_path.exists():
        raise FileNotFoundError(f".mq5 file not found: {ea_mq5_path}")

    # Load necessary MT5 paths from your config/util
    paths = load_paths()
    editor_path = paths["MT5_META_EDITOR_EXE"]
    if not editor_path.exists():
        raise FileNotFoundError(f"MetaEditor not found at: {editor_path}")

    # Figure out the .mq5's path relative to MQL5 directory
    rel_mq5_path = ea_mq5_path.relative_to(ea_mq5_path.parents[ea_mq5_path.parts.index("MQL5")])
    working_dir = ea_mq5_path.parents[ea_mq5_path.parts.index("MQL5")]

    # Define the .ex5 output file path
    ea_ex5_path = ea_mq5_path.with_suffix(".ex5")

    # Delete any previous .ex5 output before compiling
    if ea_ex5_path.exists():
        ea_ex5_path.unlink()
        logger.debug(f"Deleted old compiled file: {ea_ex5_path.name}")

    # Build MetaEditor CLI command for compilation
    command = [
        str(editor_path),
        f"/compile:{rel_mq5_path.as_posix()}",
    ]

    # Run MetaEditor as a subprocess
    logger.info(f"Compiling: {rel_mq5_path}")
    result = subprocess.run(command, cwd=working_dir, capture_output=True, text=True)

    # Check if .ex5 was generated successfully
    if ea_ex5_path.exists():
        logger.info(f"Compilation succeeded: {ea_ex5_path.name}")

    else:
        logger.error(f"Compilation failed for {ea_mq5_path.name}")

        # Log the stdout and stderr for debugging compilation problems
        logger.debug(f"stdout:\n{result.stdout}")
        logger.debug(f"stderr:\n{result.stderr}")
