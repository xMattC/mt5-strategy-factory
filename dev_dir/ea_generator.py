from pathlib import Path
from jinja2 import Template
import yaml


def generate_all_eas(template_path: Path, indicator_dir: Path, output_dir: Path):
    """
    Generate all EAs from YAML indicator definitions using a Jinja2 template.

    param template_path: Path to the Jinja2 template file
    param indicator_dir: Directory containing YAML indicator files
    param output_dir: Directory where generated .mq5 files will be saved
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(template_path, "r") as f:
        template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)

    for yaml_file in indicator_dir.glob("*.yaml"):
        with open(yaml_file, "r") as f:
            config = yaml.safe_load(f)

        indicator_name = list(config.keys())[0]
        data = config[indicator_name]

        # Generate code and write file
        generate_code(yaml_file, template, indicator_name, data, output_dir)


def generate_code(yaml_path: Path, template: Template, indicator_name: str, data: dict, output_dir: Path):
    input_lines = []
    custom_enums = {}

    if "inputs" in data:
        for k, v in data["inputs"].items():
            val = v["default"]
            typ = v["type"]

            if "enum_values" in v:
                custom_enums.setdefault(typ, {}).update(v["enum_values"])

            if isinstance(val, int):
                line = f"input int {k} = {val};"
            elif isinstance(val, float):
                line = f"input double {k} = {val};"
            else:
                line = f"input {typ} {k} = {val};"

            input_lines.append(line)

    enum_definitions = []
    if "enums" in data:
        for enum_type, values in data["enums"].items():
            lines = [f"enum {enum_type} {{"]
            lines += [f"    {v}," for v in values]
            lines.append("};\n")
            enum_definitions.append("\n".join(lines))

    rendered = template.render(
        indicator_name=indicator_name,
        indicator_path=data["indicator_path"],
        input_lines=input_lines,
        enum_definitions=enum_definitions,
        inputs=[k for k in data["inputs"]],
        buffers=data.get("buffers", []),
        base_conditions=data.get("base_conditions", {"long": "false", "short": "false"}),
        includes=data.get("includes", [])
    )

    output_file = output_dir / f"{yaml_path.stem}.mq5"
    with open(output_file, "w") as f:
        f.write(rendered)

    print(f"[INFO] Generated EA: {output_file}")
