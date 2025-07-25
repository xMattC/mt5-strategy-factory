import logging
import yaml
import importlib
from pathlib import Path
from jinja2 import Template

logger = logging.getLogger(__name__)


def import_from_string(import_path: str):
    """Dynamically import a function or class from a string."""
    module_path, func_name = import_path.rsplit('.', 1)
    mod = importlib.import_module(module_path)
    return getattr(mod, func_name)


def load_template(tmpl):
    """Load and return a Jinja2 Template from a file path or return the Template object as is."""
    if isinstance(tmpl, (str, Path)):
        with open(tmpl, "r") as f:
            return Template(f.read(), trim_blocks=True, lstrip_blocks=True)
    return tmpl


def load_render_func(rf):
    """Load the render function, either from string or directly."""
    if isinstance(rf, str):
        return import_from_string(rf)
    return rf


def load_indicator_data(indicator_yaml_file: Path) -> tuple[str, dict]:
    """ Load and validate a single-indicator YAML configuration file.

    This function expects the YAML file to have exactly one top-level key, representing the indicator name, with its
    configuration as the value.

    Example YAML structure:
        MyIndicator:
          indicator_path: "/path/to/indicator.ex5"
          inputs:
            some_input: 5
          buffers: [0, 1]

    param indicator_yaml_file: Path to the indicator YAML config file.
    return: A tuple (indicator_name, data), where indicator_name is a string and data is a dict of its configuration.
    raises: ValueError if the YAML file does not contain exactly one indicator.
    """
    # Open the YAML file and parse its contents.
    with open(indicator_yaml_file, "r") as f:
        config = yaml.safe_load(f)

    # Ensure the loaded config is a dict with exactly one top-level key.
    if not isinstance(config, dict) or len(config) != 1:
        raise ValueError(
            f"{indicator_yaml_file.name} should have a single top-level indicator (found "
            f"{len(config) if isinstance(config, dict) else 'non-dict'})."
        )

    # Convert the dictionary's items to a list, so we can access the first item directly.
    items = list(config.items())

    # The first item is a tuple: (indicator_name, data).
    indicator_name = items[0][0]
    data = items[0][1]

    return indicator_name, data
