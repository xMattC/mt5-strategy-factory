from typing import Union, List
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


def load_whitelist(source: Union[Path, str]) -> List[str]:
    """Load the whitelist from a YAML file at the given path.

    param source: Path or str to whitelist YAML file
    return: List of whitelisted symbols
    """
    white_list_path = Path(source)
    with open(white_list_path, "r") as f:
        data = yaml.safe_load(f)

    # Support both: dict with 'whitelist' key or direct list
    if isinstance(data, dict) and "whitelist" in data:
        whitelist = data["whitelist"]
    elif isinstance(data, list):
        whitelist = data
    else:
        raise ValueError(
            f"{white_list_path} must contain a YAML list or a 'whitelist' key with a list of symbols."
        )

    if not isinstance(whitelist, list):
        raise ValueError("Whitelist must be a list of symbols.")

    return whitelist
