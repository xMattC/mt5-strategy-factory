import logging
from pathlib import Path

import yaml
from jinja2 import Template

from src.path_config import load_paths

logger = logging.getLogger(__name__)


def generate_all_eas(ea_dir: Path, ea_template_path: Path) -> None:
    """
    Generate all EAs from YAML indicator definitions using a Jinja2 template.

    param ea_dir: Directory where generated .mq5 files will be saved
    param ea_template_path: Path to the Jinja2 EA template file
    """
    ea_dir.mkdir(parents=True, exist_ok=True)
    paths = load_paths()
    indicator_dir = paths["INDICATOR_DIR"]

    logger.info(f"Generating EAs using template: {ea_template_path}")
    logger.info(f"Reading indicators from: {indicator_dir}")
    logger.info(f"Saving generated .mq5 files to: {ea_dir}")

    try:
        with open(ea_template_path, "r") as f:
            template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)
    except Exception as e:
        logger.error(f"Failed to load EA template: {ea_template_path}")
        raise e

    yaml_files = list(indicator_dir.glob("*.yaml"))
    if not yaml_files:
        logger.warning("No indicator YAML files found.")
        return

    for yaml_file in yaml_files:
        with open(yaml_file, "r") as f:
            config = yaml.safe_load(f)

        indicator_name = list(config.keys())[0]
        data = config[indicator_name]
        generate_code(yaml_file, template, indicator_name, data, ea_dir)


def generate_code(yaml_path: Path, template: Template, indicator_name: str,
                  data: dict, ea_dir: Path) -> None:
    """
    Generate a single EA .mq5 file from template and YAML config.

    param yaml_path: Path to the source YAML file
    param template: Compiled Jinja2 template
    param indicator_name: Name of the indicator (from YAML key)
    param data: Parsed YAML content (dict for this indicator)
    param ea_dir: Output directory for .mq5 file
    """
    logger.debug(f"Generating EA for: {indicator_name} from YAML: {yaml_path.name}")
    input_lines = []
    custom_enums = {}

    if "inputs" in data:
        for var_name, props in data["inputs"].items():
            val = props["default"]
            typ = props["type"]

            if "enum_values" in props:
                custom_enums.setdefault(typ, {}).update(props["enum_values"])

            if isinstance(val, int):
                line = f"input int {var_name} = {val};"
            elif isinstance(val, float):
                line = f"input double {var_name} = {val};"
            else:
                line = f"input {typ} {var_name} = {val};"

            input_lines.append(line)

    enum_definitions = []
    if "enums" in data:
        for enum_type, values in data["enums"].items():
            lines = [f"enum {enum_type} {{"] + [f"    {v}," for v in values] + ["};\n"]
            enum_definitions.append("\n".join(lines))

    rendered = template.render(
        indicator_name=indicator_name,
        indicator_path=data["indicator_path"],
        input_lines=input_lines,
        enum_definitions=enum_definitions,
        inputs=[k for k in data.get("inputs", {})],
        buffers=data.get("buffers", []),
        base_conditions=data.get("base_conditions", {"long": "false", "short": "false"}),
        includes=data.get("includes", [])
    )

    output_file = ea_dir / f"{yaml_path.stem}.mq5"
    with open(output_file, "w") as f:
        f.write(rendered)

    logger.info(f"Generated EA: {output_file}")
