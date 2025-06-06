from pathlib import Path
import logging
import yaml

from meta_strategist.utils import load_paths
from meta_strategist.utils import render_template  # Assumes render_template is defined here

from .project_code_name import generate_next_project_codename
from .project_yaml_files import write_whitelist_yaml, write_make_stage_yaml_script

logger = logging.getLogger(__name__)


def create_new_project(pipeline: str, pantheon_filter: str = None) -> Path:
    """
    Create a new project directory with a sequential codename and populate it with a default configuration and run
    script.

    pantheon_filter : str, optional
        If provided, selects the next codename from a specific mythological pantheon. Valid options are:
        ['greek', 'norse', 'roman', 'egyptian', 'aztec', 'hindu', 'celtic', 'slavic'].
        If None, chooses from all pantheons at random.
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

        # create project config file
        config_dest = project_dir / f"{run_name}_config.yaml"
        with open(config_dest, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, sort_keys=False)

        # Create project run file
        run_file = project_dir / f"{run_name}_run.py"
        run_file_code = render_template("run_script.j2", {"run_name": run_name})
        run_file.write_text(run_file_code)

        # Place make_stage_yaml.py at the run_dir level
        write_make_stage_yaml_script(project_dir)

        # Place whitelist.yaml at the run_dir level
        write_whitelist_yaml(project_dir)

        logger.info(f"Created project structure in: {project_dir}")
        return project_dir

    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise


if __name__ == "__main__":
    create_new_project()
