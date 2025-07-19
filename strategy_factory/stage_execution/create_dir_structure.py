import logging
from pathlib import Path

from strategy_factory.utils.pathing import load_paths

logger = logging.getLogger(__name__)


def create_dir_structure(run_name: str, indicator_type: str) -> Path:
    """ Create standard directory structure for a run, and drop make_stage_yaml.py in the run root.

    param run_name: The run (project) name (e.g. 'Apollo')
    param indicator_type: The phase/stage name (e.g. 'Trigger')
    return: Path to the run's indicator_type subdirectory
    """
    paths = load_paths()
    base_path = paths["PRO_ROOT"]
    run_dir = base_path / "outputs" / run_name
    indi_path = run_dir / indicator_type

    (indi_path / "experts").mkdir(parents=True, exist_ok=True)
    (indi_path / "ini_files").mkdir(parents=True, exist_ok=True)
    (indi_path / "results").mkdir(parents=True, exist_ok=True)

    logger.info(f"Created directory structure under: {indi_path}")

    return indi_path


if __name__ == "__main__":
    create_dir_structure("2Apollo", "Trigger")
