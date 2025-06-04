import yaml
from pathlib import Path


def load_whitelist(project_root: Path) -> list:
    """Load the white_list from white_list.yaml at the given root path."""
    white_list_path = project_root / "white_list.yaml"
    with open(white_list_path, "r") as f:
        data = yaml.safe_load(f)
    # Defensive: ensure 'white_list' exists and is a list
    if not isinstance(data.get("white_list"), list):
        raise ValueError("white_list.yaml must contain a 'white_list' key with a list of symbols.")
    return data["white_list"]
