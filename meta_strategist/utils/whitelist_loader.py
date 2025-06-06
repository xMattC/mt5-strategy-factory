import yaml
from pathlib import Path

from pathlib import Path
from typing import List, Union


def load_whitelist(source: Union[Path, str]) -> List[str]:
    """
    Load the whitelist from a YAML file at the given path, or return ["Symbol"] if requested.

    param source: Path to whitelist YAML, or the string "CHART_SYMBOL_ONLY" to load the chart symbol only
    return: List of whitelisted symbols
    """
    if isinstance(source, str) and source.upper() == "CHART_SYMBOL_ONLY":
        return ["Symbol()"]  # MQL5/MT5 chart symbol variable

    # Else, treat as a file path (either Path or str)
    white_list_path = Path(source)
    with open(white_list_path, "r") as f:
        data = yaml.safe_load(f)
    # Defensive: ensure 'whitelist' exists and is a list
    if not isinstance(data.get("whitelist"), list):
        raise ValueError("whitelist.yaml must contain a 'whitelist' key with a list of symbols.")
    return data["whitelist"]
