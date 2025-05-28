import logging
from meta_strategist.utils.pathing import load_paths
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


def load_trigger_data(run_name: str) -> tuple[str, dict]:
    """Load optimised trigger indicator parameters and merge with base YAML.

    This reads the optimised values from the_trigger.yaml for this run,
    merges them into the original indicator YAML structure, and returns both.

    param run_name: Name of the optimisation run (folder in OUTPUT_DIR)
    return: (indicator_name, merged_dict)
    """
    # 1. Read optimised trigger YAML, which should only contain one indicator
    trigger_yaml_path = load_paths()["OUTPUT_DIR"] / run_name / "Trigger" / "the_trigger.yaml"

    with open(trigger_yaml_path, "r") as f:
        trigger_result = yaml.safe_load(f)
    indicator_name = next(iter(trigger_result))
    optimised_params = trigger_result[indicator_name]

    # 2. Load the original YAML for this indicator from INDICATOR_DIR
    indicator_dir = load_paths()["INDICATOR_DIR"]
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



