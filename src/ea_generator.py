from pathlib import Path
from jinja2 import Template
import yaml
from src.path_config import load_paths


def generate_all_eas(ea_dir: Path) -> None:
    """ Generate all EAs from YAML indicator definitions using a Jinja2 template.

    param ea_dir: Directory where generated .mq5 files will be saved
    """
    ea_dir.mkdir(parents=True, exist_ok=True)

    paths = load_paths()
    template_path = paths["TEMPLATE_DIR"] / 'template_c1_mq5.j2'
    indicator_dir = paths["INDICATOR_DIR"]

    # Load and compile the Jinja2 template
    with open(template_path, "r") as f:
        template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)

    # Process each YAML file and generate corresponding EA
    for yaml_file in indicator_dir.glob("*.yaml"):
        with open(yaml_file, "r") as f:
            config = yaml.safe_load(f)

        # Expecting YAML to have one top-level key: the indicator name
        indicator_name = list(config.keys())[0]
        data = config[indicator_name]

        # Generate EA source code and write it to disk
        generate_code(yaml_file, template, indicator_name, data, ea_dir)


def generate_code(yaml_path: Path, template: Template, indicator_name: str, data: dict, ea_dir: Path) -> None:
    """ Generate a single EA .mq5 file from template and YAML config.

    param yaml_path: Path to the source YAML file
    param template: Compiled Jinja2 template
    param indicator_name: Name of the indicator (from YAML key)
    param data: Parsed YAML content (dict for this indicator)
    param ea_dir: Output directory for .mq5 file
    """
    input_lines = []       # Stores formatted `input` declarations
    custom_enums = {}      # Optionally gather any enums from input definitions

    # Process "inputs" section and generate variable declarations
    if "inputs" in data:
        for var_name, props in data["inputs"].items():
            val = props["default"]
            typ = props["type"]

            # If the input defines enum values, track them for potential use
            if "enum_values" in props:
                custom_enums.setdefault(typ, {}).update(props["enum_values"])

            # Generate the appropriate MQL5 input declaration
            if isinstance(val, int):
                line = f"input int {var_name} = {val};"
            elif isinstance(val, float):
                line = f"input double {var_name} = {val};"
            else:
                line = f"input {typ} {var_name} = {val};"

            input_lines.append(line)

    # Process "enums" section and generate MQL5 enum definitions
    enum_definitions = []
    if "enums" in data:
        for enum_type, values in data["enums"].items():
            lines = [f"enum {enum_type} {{"] + [f"    {v}," for v in values] + ["};\n"]
            enum_definitions.append("\n".join(lines))

    # Render the final EA source code using the template
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

    # Write the generated .mq5 file
    output_file = ea_dir / f"{yaml_path.stem}.mq5"
    with open(output_file, "w") as f:
        f.write(rendered)

    print(f"[INFO] Generated EA: {output_file}")
