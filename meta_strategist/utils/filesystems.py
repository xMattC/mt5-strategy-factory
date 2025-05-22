import yaml
import logging
from pathlib import Path
from meta_strategist.generators.ini_generator import IniConfig
from meta_strategist.utils.pathing import load_paths

logger = logging.getLogger(__name__)


def load_config_from_yaml(config_path: Path) -> IniConfig:
    """Load a YAML config and return an IniConfig instance."""
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    return IniConfig(**data)


import logging
from pathlib import Path
from meta_strategist.generators.ini_generator import IniConfig
from meta_strategist.utils.pathing import load_paths

logger = logging.getLogger(__name__)


def create_dir_structure(run_name: str, indicator_type: str) -> Path:
    """
    Create standard directory structure for a run, and drop make_stage_yaml.py in the run root.

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

    # Place make_stage_yaml.py at the run_dir level
    _write_make_stage_yaml_script(run_dir)

    logger.info(f"Created directory structure under: {indi_path}")
    return indi_path


def _write_make_stage_yaml_script(run_dir: Path):
    """
    Drop a default make_stage_yaml.py script into run_dir.
    Do nothing if file already exists.
    """
    script_path = run_dir / "make_stage_yaml.py"
    if script_path.exists():
        print(f"{script_path} already exists. Delete it to remake.")
        return

    content = (
        "from meta_strategist.utils.stage_yaml_maker import maker\n"
        "from pathlib import Path\n\n"
        "if __name__ == \"__main__\":\n"
        "    run_dir = Path(__file__).parent.resolve()\n"
        "    maker(run_dir=run_dir, phase=\"trigger\", indicator=\"ASO\")\n"
    )
    script_path.parent.mkdir(parents=True, exist_ok=True)
    with open(script_path, "w") as f:
        f.write(content)

    print(f"make_stage_yaml.py written to: {script_path}")

if __name__ == "__main__":
    create_dir_structure("2Apollo", "Trigger")