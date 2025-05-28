import random
import string
from pathlib import Path
import logging
import yaml

from meta_strategist.utils import load_paths
from meta_strategist.utils import render_template  # Assumes render_template is defined here

logger = logging.getLogger(__name__)


def load_pantheons() -> dict:
    """Load pantheon data from the YAML file and convert to (name, description) tuples per pantheon."""
    # paths = load_paths()
    # Find the directory this script is in
    script_dir = Path(__file__).parent
    # Compose the path to the YAML file relative to this script
    name_file = script_dir / "project_names.yaml"
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


def create_new_project(pantheon_filter: str = None) -> Path:
    """
    Create a new project directory with a sequential codename and populate it with
    a default configuration and run script.

    Parameters
    ----------
    pantheon_filter : str, optional
        If provided, selects the next codename from a specific mythological pantheon. Valid options are:
        ['greek', 'norse', 'roman', 'egyptian', 'aztec', 'hindu', 'celtic', 'slavic'].
        If None, chooses from all pantheons at random.

    Returns
    -------
    Path
        The path to the newly created project directory.

    """
    run_name = generate_next_project_codename(pantheon_filter)
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
        logger.error(f"Project directory already exists: {project_dir}")
        raise

    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise


if __name__ == "__main__":
    create_new_project()
