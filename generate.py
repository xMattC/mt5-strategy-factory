import yaml
from jinja2 import Template
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "template_mq5.j2"
INDICATOR_DIR = Path("indicators")
OUTPUT_DIR = Path("outputs_dir")


def generate_code(yaml_path, template: Template):
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    indicator_name = list(config.keys())[0]
    data = config[indicator_name]

    input_lines = []
    if "inputs" in data:
        for k, v in data["inputs"].items():
            val = v["default"]
            if isinstance(val, int):
                line = f"input int {k} = {val};"
            elif isinstance(val, float):
                line = f"input double {k} = {val};"
            else:
                line = f"input ENUM_{k} {k} = {val};"
            input_lines.append(line)

    rendered = template.render(
        indicator_name=indicator_name,
        indicator_path=data["indicator_path"],
        input_lines=input_lines,
        inputs=[k for k in data["inputs"]],
        buffers=data.get("buffers", []),
        base_conditions=data.get("base_conditions", {"long": "false", "short": "false"})
    )

    output_file = OUTPUT_DIR / (yaml_path.stem + ".mq5")
    with open(output_file, "w") as f:
        f.write(rendered)

    print(f"Generated: {output_file}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(TEMPLATE_PATH, "r") as f:
        template = Template(f.read())

    for yaml_file in INDICATOR_DIR.glob("*.yaml"):
        generate_code(yaml_file, template)


if __name__ == "__main__":
    main()
