import yaml

from meta_strategist.generators.ini_generator import IniConfig

import logging
from pathlib import Path
from meta_strategist.utils.pathing import load_paths

logger = logging.getLogger(__name__)


def load_config_from_yaml(config_path: Path) -> IniConfig:
    """Load a YAML config and return an IniConfig instance."""
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    return IniConfig(**data)


def create_dir_structure(run_name: str, indicator_type: str) -> Path:
    """Create a standardized directory structure for a given run and return the base path.

    param run_name: Name of the run (e.g., 'zuse', 'test1')
    param indicator_type: Indicator type folder (e.g., 'C1', 'Volume')
    return: Path to the run's base output directory
    """
    paths = load_paths()
    base_path = paths["PRO_ROOT"]
    indi_path = base_path / "outputs" / run_name / indicator_type

    (indi_path / "experts").mkdir(parents=True, exist_ok=True)
    (indi_path / "ini_files").mkdir(parents=True, exist_ok=True)
    (indi_path / "results").mkdir(parents=True, exist_ok=True)

    logger.info(f"Created directory structure under: {indi_path}")
    return indi_path
