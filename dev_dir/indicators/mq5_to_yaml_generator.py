import re
import yaml
from pathlib import Path


def normalize_code(text):
    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        # Collapse multiple spaces into one
        line = re.sub(r'\s{2,}', ' ', line)
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def extract_inputs(code: str):
    inputs = {}
    input_pattern = re.compile(
        r"input\s+(?P<type>[a-zA-Z_][\w<>]*)\s+"
        r"(?P<name>[a-zA-Z_][\w]*)\s*=\s*"
        r"(?P<default>[^;]+);"
    )

    for match in input_pattern.finditer(code):
        typ = match.group("type").strip()
        name = match.group("name").strip()
        default_raw = match.group("default").strip()

        entry = {"type": typ, "default": None, "optimize": False}

        if typ in ("int", "uint"):
            try:
                entry["default"] = int(re.search(r"-?\d+", default_raw).group())
            except:
                entry["default"] = 0
            entry["type"] = "int"
            entry.update({"min": 1, "max": 50, "step": 1, "optimize": True})
        elif typ == "double":
            try:
                entry["default"] = float(re.search(r"-?\d+(\.\d+)?", default_raw).group())
            except:
                entry["default"] = 0.0
            entry.update({"min": 0.1, "max": 5.0, "step": 0.1, "optimize": True})
        else:
            entry["default"] = default_raw
            entry["optimize"] = False

        inputs[name] = entry

    return inputs


def extract_enums(code: str):
    enums = {}
    enum_pattern = re.compile(r"enum\s+([a-zA-Z_][\w]*)\s*{([^}]+)};", re.MULTILINE | re.DOTALL)
    for match in enum_pattern.finditer(code):
        enum_name, body = match.groups()
        members = {}
        for line in body.strip().splitlines():
            if not line.strip():
                continue
            parts = line.strip().split("//")
            name = parts[0].replace(",", "").strip()
            comment = parts[1].strip() if len(parts) > 1 else name
            members[name] = comment
        enums[enum_name] = members
    return enums


def extract_buffers(code: str):
    buffers = []
    buffer_pattern = re.compile(r"SetIndexBuffer\((\d+),\s*([a-zA-Z_][\w]*)")
    seen = set()
    for match in buffer_pattern.finditer(code):
        index, name = match.groups()
        if name not in seen:
            seen.add(name)
            buffers.append({"name": name, "index": int(index)})
    return buffers


def extract_includes(code: str):
    includes = []
    include_pattern = re.compile(r'#include\s+<(.+?)>')
    for match in include_pattern.finditer(code):
        includes.append(match.group(1))
    return includes


def generate_yaml(name: str, code: str):
    config = {
        name: {
            "custom": True,
            "indicator_path": f"MyIndicators/{name}.ex5",
            "inputs": extract_inputs(code),
            "buffers": extract_buffers(code),
            "base_conditions": {
                "long": "",
                "short": ""
            }
        }
    }

    enums = extract_enums(code)
    if enums:
        config[name]["enums"] = enums

    includes = extract_includes(code)
    if includes:
        config[name]["includes"] = includes

    return config


def convert_mq5_to_yaml(input_path: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_file() and input_path.suffix == ".mq5":
        mq5_files = [input_path]
    else:
        mq5_files = list(input_path.glob("*.mq5"))

    for mq5_file in mq5_files:
        name = mq5_file.stem
        code = mq5_file.read_text(encoding="utf-8", errors="ignore")
        code = normalize_code(code)
        yaml_data = generate_yaml(name, code)
        output_path = output_dir / f"{name}.yaml"
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, sort_keys=False)
        print(f"Generated: {output_path}")


if __name__ == "__main__":
    output_dir = Path(
        r"/outputs_dir")
    indi_dir = Path(
        r"C:\Users\mkcor\AppData\Roaming\MetaQuotes\Terminal\49CDDEAA95A409ED22BD2287BB67CB9C\MQL5\Indicators\MyIndicators")

    mq5_file = indi_dir / "ASO.mq5"
    convert_mq5_to_yaml(mq5_file, output_dir)


