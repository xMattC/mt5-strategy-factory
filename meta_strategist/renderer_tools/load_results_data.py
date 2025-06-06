import logging
from meta_strategist.utils.pathing import load_paths
import yaml

from meta_strategist.stage_execution.stage_config import StageConfig

logger = logging.getLogger(__name__)


def load_results_data(run_name: str, stage: StageConfig) -> tuple[str, dict]:
    """Load optimised indicator parameters for any stage and merge with base YAML.

    Reads the optimised values from the results YAML for this run/stage,
    merges them into the original indicator YAML structure, and returns both.

    param run_name: Name of the optimisation run (folder in OUTPUT_DIR)
    param stage: Stage object (e.g., get_stage("Trigger"))
    return: (indicator_name, merged_dict)
    """
    # 1. Build path to the results YAML for this stage
    results_filename = f"the_{stage.name.lower()}.yaml"
    results_path = load_paths()["OUTPUT_DIR"] / run_name / stage.name / results_filename

    with open(results_path, "r") as f:
        result_data = yaml.safe_load(f)

    indicator_name = next(iter(result_data))
    optimised_params = result_data[indicator_name]

    # 2. Load the original YAML for this indicator from the *stage subdirectory* of INDICATOR_DIR
    indicator_dir = load_paths()["INDICATOR_DIR"]
    if getattr(stage, "indi_dir", None):
        indicator_dir = indicator_dir / stage.indi_dir
    base_yaml_path = indicator_dir / f"{indicator_name}.yaml"

    with open(base_yaml_path, "r") as f:
        base = yaml.safe_load(f)

    base_data = base[indicator_name]

    # 3. Overwrite base inputs with optimised defaults, or add them if missing
    for k, v in optimised_params.items():
        if "inputs" in base_data and k in base_data["inputs"]:
            base_data["inputs"][k]["default"] = v
        else:
            # If key is new, add with minimal info; adjust as needed for your schema
            if "inputs" not in base_data:
                base_data["inputs"] = {}
            base_data["inputs"][k] = {"default": v, "type": type(v).__name__}

    return indicator_name, base_data

