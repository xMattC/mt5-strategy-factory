import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_compiled_indicators(expert_dir: Path) -> list[str]:
    """ Scan a directory for compiled EAs and report missing .ex5 files.

    param expert_dir: Directory containing .mq5/.ex5 files
    return: List of names of compiled indicators (present as both .mq5 and .ex5)
    """
    _logger = logging.getLogger(__name__)

    # List to store indicator names that are fully compiled (both .mq5 and .ex5 present)
    compiled_indicators = []

    # List to collect indicator names missing their .ex5 compiled binary
    un_compiled = []

    # Get all .mq5 (source) files in the directory
    mq5_files = list(expert_dir.glob("*.mq5"))

    # Create a set of all .ex5 (compiled binary) file names (without extension)
    ex5_files = {f.stem for f in expert_dir.glob("*.ex5")}

    # Check each .mq5 source file to see if the corresponding .ex5 exists
    for mq5_file in mq5_files:
        base_name = mq5_file.stem
        if base_name in ex5_files:
            # Both .mq5 and .ex5 exist; EA is considered compiled
            compiled_indicators.append(base_name)
        else:
            # .mq5 exists but .ex5 does not; EA needs attention
            _logger.warning(f"MQ5 exists but EX5 missing for: {base_name}")
            un_compiled.append(base_name)

    # If any indicators are missing their .ex5, write their names to a debug report
    if un_compiled:
        report_path = expert_dir / "00_un_compiled.txt"
        with open(report_path, "w") as f:
            f.write("Indicators with missing .ex5:\n")
            f.writelines(f"- {name}\n" for name in sorted(un_compiled))
        _logger.info(f"Wrote un-compiled list to: {report_path}")

    # Log overall summary for visibility
    if not compiled_indicators:
        _logger.info("No compiled indicators (.ex5) found.")
    else:
        _logger.info(f"Found {len(compiled_indicators)} compiled indicators.")

    # Return only the names of indicators that are present and compiled
    return compiled_indicators
