import logging
from meta_strategist.utils.pathing import load_paths
import yaml
from pathlib import Path

from meta_strategist.pipeline import Stage

logger = logging.getLogger(__name__)


def load_indicator_data(yaml_file: Path) -> tuple[str, dict]:
    """ Load and validate a single-indicator YAML configuration file.

    This function expects the YAML file to have exactly one top-level key, representing the indicator name, with its
    configuration as the value.

    Example YAML structure:
        MyIndicator:
          indicator_path: "/path/to/indicator.ex5"
          inputs:
            some_input: 5
          buffers: [0, 1]

    param yaml_file: Path to the indicator YAML config file.
    return: A tuple (indicator_name, data), where indicator_name is a string and data is a dict of its configuration.
    raises: ValueError if the YAML file does not contain exactly one indicator.
    """
    # Open the YAML file and parse its contents.
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)

    # Ensure the loaded config is a dict with exactly one top-level key.
    if not isinstance(config, dict) or len(config) != 1:
        raise ValueError(
            f"{yaml_file.name} should have a single top-level indicator (found "
            f"{len(config) if isinstance(config, dict) else 'non-dict'})."
        )

    # Convert the dictionary's items to a list, so we can access the first item directly.
    items = list(config.items())

    # The first item is a tuple: (indicator_name, data).
    indicator_name = items[0][0]
    data = items[0][1]

    return indicator_name, data
