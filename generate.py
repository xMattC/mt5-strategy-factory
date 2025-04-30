import yaml
from jinja2 import Template
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"  # Path to templates
INDICATOR_DIR = Path("indicators")  # Path to indicator YAML files
OUTPUT_DIR = Path("outputs_dir")  # Path to the output MQL5 files


def generate_code(yaml_path, template: Template, indicator_name: str, data: dict):
    # Collect input definitions
    input_lines = []
    if "inputs" in data:
        for k, v in data["inputs"].items():
            val = v["default"]
            if isinstance(val, int):
                line = f"input int {k} = {val};"
            elif isinstance(val, float):
                line = f"input double {k} = {val};"
            else:
                line = f"input {v['type']} {k} = {val};"
            input_lines.append(line)

    # Render the MQL5 file content
    rendered = template.render(
        indicator_name=indicator_name,
        indicator_path=data["indicator_path"],
        input_lines=input_lines,
        inputs=[k for k in data["inputs"]],
        buffers=data.get("buffers", []),
        base_conditions=data.get("base_conditions", {"long": "false", "short": "false"})
    )

    # Output file path and writing to it
    output_file = OUTPUT_DIR / (yaml_path.stem + ".mq5")
    with open(output_file, "w") as f:
        f.write(rendered)

    print(f"Generated: {output_file}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Loop through each YAML file in the indicators directory
    for yaml_file in INDICATOR_DIR.glob("*.yaml"):
        with open(yaml_file, "r") as f:
            config = yaml.safe_load(f)

        indicator_name = list(config.keys())[0]
        data = config[indicator_name]

        # Use the general template for all indicators
        template_path = TEMPLATES_DIR / "template_mq5.j2"  # General template for all indicators

        # Load the template
        with open(template_path, "r") as f:
            template = Template(f.read())

        # Generate the MQL5 code for this indicator
        generate_code(yaml_file, template, indicator_name, data)


if __name__ == "__main__":
    main()
