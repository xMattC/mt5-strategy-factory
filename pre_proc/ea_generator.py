import yaml
from jinja2 import Template
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"  # Path to templates
INDICATOR_DIR = Path("../indicators")  # Path to indicator YAML files
OUTPUT_DIR = Path("../mt5_pipeline/compiled_ea_dir")  # Path to the output MQL5 files


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Loop through each YAML file in the indicators directory
    for yaml_file in INDICATOR_DIR.glob("*.yaml"):
        with open(yaml_file, "r") as f:
            config = yaml.safe_load(f)

        indicator_name = list(config.keys())[0]
        data = config[indicator_name]

        # Use the general template for all indicators
        template_path = "template_c1_mq5.j2"  # General template for all indicators

        # Load the template
        with open(template_path, "r") as f:
            template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)

        # Generate the MQL5 code for this indicator
        generate_code(yaml_file, template, indicator_name, data)


def generate_code(yaml_path, template, indicator_name: str, data: dict):
    input_lines = []
    custom_enums = {}  # Map: enum_type -> dict of enum_name: comment

    # Handle inputs and enum definitions
    if "inputs" in data:
        for k, v in data["inputs"].items():
            val = v["default"]
            typ = v["type"]

            # Check for custom enums in inputs
            if "enum_values" in v:
                if typ not in custom_enums:
                    custom_enums[typ] = {}
                custom_enums[typ].update(v["enum_values"])

            # Input line generation
            if isinstance(val, int):
                line = f"input int {k} = {val};"
            elif isinstance(val, float):
                line = f"input double {k} = {val};"
            else:
                line = f"input {typ} {k} = {val};"
            input_lines.append(line)

    # Generate enum declaration blocks
    enum_definitions = []
    if "enums" in data:
        for enum_type, values in data["enums"].items():
            lines = [f"enum {enum_type} {{"]
            for value in values:
                lines.append(f"    {value},")
            lines.append("};\n")
            enum_definitions.append("\n".join(lines))

    includes = data.get("includes", [])

    # Render the template
    rendered = template.render(
        indicator_name=indicator_name,
        indicator_path=data["indicator_path"],
        input_lines=input_lines,
        enum_definitions=enum_definitions,
        inputs=[k for k in data["inputs"]],
        buffers=data.get("buffers", []),
        base_conditions=data.get("base_conditions", {"long": "false", "short": "false"}),
        includes=includes
    )

    # Output path
    output_file = OUTPUT_DIR / (yaml_path.stem + ".mq5")
    with open(output_file, "w") as f:
        f.write(rendered)

    print(f"Generated: {output_file}")


if __name__ == "__main__":
    main()
