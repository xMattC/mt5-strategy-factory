import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_inputs_from_input_yaml(yaml_path: Path, expected_key: str) -> dict:
    """Extract and merge 'indicator_inputs' and 'logic_inputs' from a YAML indicator file.

    Parameters:
    - yaml_path: Path to the .yaml file describing the indicator
    - expected_key: Expected top-level key (indicator name) in the YAML

    Returns:
    - Dictionary of combined input parameter definitions
    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")

    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    top_key = next(iter(data))
    if top_key.lower() != expected_key.lower():
        logger.warning(f"Top-level key '{top_key}' does not match expected name '{expected_key}'")

    indi_data = data[top_key]

    indicator_inputs = indi_data.get("indicator_inputs") or {}
    logic_inputs = indi_data.get("logic_inputs") or {}

    if not isinstance(indicator_inputs, dict):
        raise ValueError(f"'indicator_inputs' in {yaml_path.name} must be a dictionary")
    if not isinstance(logic_inputs, dict):
        raise ValueError(f"'logic_inputs' in {yaml_path.name} must be a dictionary")

    # Merge both dicts into a single parameter definition
    merged_inputs = {**indicator_inputs, **logic_inputs}
    return merged_inputs

