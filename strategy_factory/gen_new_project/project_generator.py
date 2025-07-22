from pathlib import Path
import logging
import shutil

from strategy_factory.utils import load_paths
from strategy_factory.gen_new_project.project_code_name import generate_next_project_codename

logger = logging.getLogger(__name__)


def create_new_project(pipeline: str, pantheon_filter: str = None) -> Path:
    """ Create a new project directory with a sequential codename and populate it with a default configuration and run
    script.

    pantheon_filter : str, optional
        If provided, selects the next codename from a specific mythological pantheon. Valid options are:
        ['greek', 'norse', 'roman', 'egyptian', 'aztec', 'hindu', 'celtic', 'slavic'].
        If None, chooses from all pantheons at random.
    """
    run_name = generate_next_project_codename(pantheon_filter)
    paths = load_paths()
    project_dir = paths["OUTPUT_DIR"] / run_name
    pipelines_dir = paths["PIPELINE_DIR"] / pipeline

    try:
        project_dir.mkdir(parents=True, exist_ok=False)

        # Copy and patch config.yaml
        config_src = pipelines_dir / "config.yaml"
        config_dst = project_dir / "config.yaml"
        with open(config_src, "r") as fin, open(config_dst, "w") as f_out:
            first_line = fin.readline()
            # Replace run_name in the first line
            if first_line.lower().startswith("run_name:"):
                f_out.write(f"run_name: {run_name}\n")
            else:
                f_out.write(first_line)
            # Copy rest of the file
            for line in fin:
                f_out.write(line)

        # Copy and rename run_template.py
        run_template_src = pipelines_dir / "run_template.py"
        run_template_dst = project_dir / f"{run_name}_run.py"
        shutil.copyfile(run_template_src, run_template_dst)

        # Copy whitelist.yaml
        whitelist_src = pipelines_dir / "whitelist.yaml"
        whitelist_dst = project_dir / "whitelist.yaml"
        shutil.copyfile(whitelist_src, whitelist_dst)

        logger.info(f"Created project structure in: {project_dir}")
        return project_dir

    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise


if __name__ == "__main__":
    create_new_project("trend_following")
