from pathlib import Path
import logging
import yaml


logger = logging.getLogger(__name__)


def write_make_stage_yaml_script(run_dir: Path):
    """
    Drop a default make_stage_yaml.py script into run_dir.
    Do nothing if file already exists.
    """
    script_path = run_dir / "make_stage_yaml.py"
    if script_path.exists():
        logger.info(f"{script_path} already exists. Delete it to remake.")
        return

    content = (
        "from strategy_factory.utils import maker\n"
        "from pathlib import Path\n\n"
        "if __name__ == \"__main__\":\n"
        "    run_dir = Path(__file__).parent.resolve()\n"
        "    maker(run_dir=run_dir, phase=\"trigger\", indicator=\"ASO\")\n"
    )
    script_path.parent.mkdir(parents=True, exist_ok=True)
    with open(script_path, "w") as f:
        f.write(content)

    logger.info(f"make_stage_yaml.py written to: {script_path}")


def write_whitelist_yaml(project_dir: Path, symbols=None, overwrite=False):
    """
    Create a whitelist.yaml file in the specified project directory.

    param project_dir: Path to the project directory where whitelist.yaml will be created
    param symbols: List of symbols to include in the whitelist. Defaults to a sample list if None.
    param overwrite: If True, will overwrite any existing whitelist.yaml. Default is False.
    """
    symbols = symbols or ["EURUSD", "AUDNZD", "EURGBP", "AUDCAD", "CHFJPY"]
    whitelist_path = project_dir / "whitelist.yaml"

    if whitelist_path.exists() and not overwrite:
        logger.info(f"{whitelist_path} already exists. Delete it or set overwrite=True to recreate.")
        return

    data = {"whitelist": symbols}
    with open(whitelist_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

    logger.info(f"whitelist.yaml written to: {whitelist_path}")

