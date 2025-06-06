import random
import string
import logging
from pathlib import Path

import yaml

from meta_strategist.utils import load_paths

logger = logging.getLogger(__name__)


def load_pantheons() -> dict:
    """Load pantheon data from the YAML file and convert to (name, description) tuples per pantheon."""
    # Determine the directory this script is in (so we can find the YAML file relative to this file)
    script_dir = Path(__file__).parent
    # Compose the path to the project_names.yaml file
    name_file = script_dir / "project_names.yaml"
    if not name_file.exists():
        raise FileNotFoundError(f"Pantheon YAML file not found at: {name_file}")

    with open(name_file, encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)

    # Convert loaded data to a dict of pantheon -> list of (name, description) tuples
    return {
        pantheon: [(entry["name"], entry["description"]) for entry in gods]
        for pantheon, gods in raw_data.items()
    }


def get_all_gods(pantheon_filter: str = None):
    """Flatten all gods into a list of (pantheon, name, description)."""
    pantheons = load_pantheons()
    pantheon_filter = pantheon_filter.lower() if pantheon_filter else None

    if pantheon_filter and pantheon_filter not in pantheons:
        raise ValueError(f"Pantheon '{pantheon_filter}' not recognised. Available: {list(pantheons)}")

    # Flatten each pantheon into a tuple with pantheon name, god name, and description
    return [
        (pantheon, name, desc)
        for pantheon, gods in pantheons.items()
        if not pantheon_filter or pantheon == pantheon_filter
        for name, desc in gods
    ]


def generate_next_project_codename(pantheon_filter: str = None) -> str:
    """Interactive generation of the next available project codename."""
    paths = load_paths()
    outputs_dir = paths["OUTPUT_DIR"]

    # Gather all existing project directory names
    existing_dirs = [f.name for f in outputs_dir.iterdir() if f.is_dir()]
    used_letters = {name[0].upper() for name in existing_dirs if name}

    all_gods = get_all_gods(pantheon_filter)

    # Two passes: first for unused letters, then wrap-around if needed
    for _ in range(2):
        for letter in string.ascii_uppercase:
            if letter not in used_letters:
                candidates = [g for g in all_gods if g[1].upper().startswith(letter)]
                if candidates:
                    while candidates:
                        pantheon, name, description = random.choice(candidates)
                        print(f"Suggested: {name} - {pantheon.capitalize()} god - {description}")
                        user_input = input("Accept this name? [Y/n]: ").strip().lower()
                        if user_input in ("", "y"):
                            return name
                        candidates.remove((pantheon, name, description))
        used_letters.clear()  # Allow wrap-around after first pass

    raise RuntimeError("No suitable god name found for project codename.")
