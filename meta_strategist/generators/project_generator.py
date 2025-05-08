import random
import string
from pathlib import Path
import logging

from meta_strategist.utils.pathing import load_paths
from meta_strategist.utils.render_template import render_template  # Assumes render_template is defined here

logger = logging.getLogger(__name__)


def load_pantheons() -> dict:
    """Load pantheon data from the YAML file and convert to (name, description) tuples per pantheon."""
    paths = load_paths()
    name_file = paths["GENERATORS_DIR"] / "project_names.yaml"
    if not name_file.exists():
        raise FileNotFoundError(f"Pantheon YAML file not found at: {name_file}")

    with open(name_file, encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)

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

    existing_dirs = [f.name for f in outputs_dir.iterdir() if f.is_dir()]
    used_letters = {name[0].upper() for name in existing_dirs if name}

    all_gods = get_all_gods(pantheon_filter)

    for _ in range(2):  # Two full passes: once to check used letters, once for wrap-around
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
        used_letters.clear()  # Allow wrap-around

    raise RuntimeError("No suitable god name found for project codename.")


import yaml

def create_new_project() -> Path:
    """Interactively generate a new project directory and populate it."""
    run_name = generate_next_project_codename()
    paths = load_paths()
    project_dir = paths["OUTPUT_DIR"] / run_name

    try:
        project_dir.mkdir(parents=True, exist_ok=False)

        # Load and update config template
        template_config_path = paths["TEMPLATE_DIR"] / "default_config.yaml"
        with open(template_config_path, encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # Update run_name in config
        config_data["run_name"] = run_name

        # Save updated config to new location
        config_dest = project_dir / f"{run_name}_config.yaml"
        with open(config_dest, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, sort_keys=False)

        # Create run file
        run_file = project_dir / f"{run_name}_run.py"
        run_file_code = render_template("run_script.j2", {"run_name": run_name})
        run_file.write_text(run_file_code)

        logger.info(f"Created project structure in: {project_dir}")
        return project_dir

    except FileExistsError:
        logger.warning(f"{run_name} project folder already exists")


if __name__ == "__main__":
    create_new_project()
