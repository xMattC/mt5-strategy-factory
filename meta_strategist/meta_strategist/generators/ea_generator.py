import logging
import subprocess
from pathlib import Path

import yaml
from jinja2 import Template

from meta_strategist.utils.pathing import load_paths

logger = logging.getLogger(__name__)

__all__ = ["generate_all_eas", "get_compiled_indicators"]


def generate_all_eas(ea_dir: Path, ea_template_path: Path) -> None:
    """ Orchestrates EA generation and compilation for all indicator YAMLs.

    param ea_dir: Directory where generated .mq5 files will be saved
    param ea_template_path: Path to the Jinja2 EA template file
    """
    ea_dir.mkdir(parents=True, exist_ok=True)
    paths = load_paths()
    indicator_dir = paths["INDICATOR_DIR"]
    terminal_path = paths["MT5_TERM_EXE"]

    template = load_template(ea_template_path)
    yaml_files = list(indicator_dir.glob("*.yaml"))

    if not yaml_files:
        logger.warning("No indicator YAML files found.")
        return

    for yaml_file in yaml_files:
        try:
            process_single_ea(yaml_file, template, ea_dir, terminal_path)
        except Exception as e:
            logger.error(f"Error processing {yaml_file.name}: {e}")


def get_compiled_indicators(expert_dir: Path) -> list[str]:
    """ Scans a directory and returns a list of indicator names with compiled .ex5 files.
    Also logs and saves a .txt file listing any .mq5 files without a corresponding .ex5.

    param expert_dir: Path to the folder containing .mq5 and .ex5 files
    return: List of indicator base names (without extension) that have been compiled
    """
    compiled_indicators = []
    un_compiled = []

    mq5_files = list(expert_dir.glob("*.mq5"))
    ex5_files = {f.stem for f in expert_dir.glob("*.ex5")}

    for mq5_file in mq5_files:
        base_name = mq5_file.stem
        if base_name in ex5_files:
            compiled_indicators.append(base_name)
        else:
            logger.warning(f"MQ5 exists but EX5 missing for: {base_name}")
            un_compiled.append(base_name)

    # Save uncompiled list if needed
    if un_compiled:
        report_path = expert_dir / "00_uncompiled.txt"
        with open(report_path, "w") as f:
            f.write("Indicators with missing .ex5:\n")
            f.writelines(f"- {name}\n" for name in sorted(un_compiled))
        logger.info(f"Wrote uncompiled list to: {report_path}")

    if not compiled_indicators:
        logger.info("No compiled indicators (.ex5) found.")
    else:
        logger.info(f"Found {len(compiled_indicators)} compiled indicators.")

    return compiled_indicators


def load_template(template_path: Path) -> Template:
    """ Load and compile a Jinja2 template for EA generation.

    param template_path: Path to the .j2 template file
    return: Compiled Jinja2 template
    """
    logger.info(f"Loading EA template from: {template_path}")
    try:
        with open(template_path, "r") as f:
            return Template(f.read(), trim_blocks=True, lstrip_blocks=True)
    except Exception as e:
        logger.error(f"Failed to load EA template: {template_path}")
        raise


def process_single_ea(yaml_file: Path, template: Template, ea_dir: Path, terminal_path: Path) -> None:
    """ Generate and compile a single EA from a YAML config file.

    param yaml_file: Path to YAML indicator definition
    param template: Compiled Jinja2 template
    param ea_dir: Output directory for the .mq5 file
    param terminal_path: Path to MT5 terminal executable
    """
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)

    indicator_name = list(config.keys())[0]
    data = config[indicator_name]

    mq5_path = generate_ea_mq5(yaml_file, template, indicator_name, data, ea_dir)
    compile_ea(mq5_path)
    logger.info(f"Compiled EA successfully: {mq5_path.name}")


def generate_ea_mq5(yaml_path: Path, template: Template, indicator_name: str,
                    data: dict, ea_dir: Path) -> Path:
    """ Generate a single EA .mq5 file from template and YAML config.

    param yaml_path: Path to the source YAML file
    param template: Compiled Jinja2 template
    param indicator_name: Name of the indicator (from YAML key)
    param data: Parsed YAML content (dict for this indicator)
    param ea_dir: Output directory for .mq5 file
    return: Path to generated .mq5 file
    """
    logger.debug(f"Generating EA for: {indicator_name} from YAML: {yaml_path.name}")

    input_lines = build_input_lines(data)
    enum_definitions = build_enum_definitions(data)

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
    return output_file


def compile_ea(ea_mq5_path: Path) -> None:
    """
    Compile an .mq5 file into .ex5 using MetaEditor.
    Deletes any previous .ex5 output before compiling.
    """
    if not ea_mq5_path.exists():
        raise FileNotFoundError(f".mq5 file not found: {ea_mq5_path}")

    paths = load_paths()
    editor_path = paths["MT5_META_EDITOR_EXE"]
    if not editor_path.exists():
        raise FileNotFoundError(f"MetaEditor not found at: {editor_path}")

    rel_mq5_path = ea_mq5_path.relative_to(ea_mq5_path.parents[ea_mq5_path.parts.index("MQL5")])
    working_dir = ea_mq5_path.parents[ea_mq5_path.parts.index("MQL5")]
    ea_ex5_path = ea_mq5_path.with_suffix(".ex5")

    # Delete previous compiled output (if it exists)
    if ea_ex5_path.exists():
        ea_ex5_path.unlink()
        logger.debug(f"Deleted old compiled file: {ea_ex5_path.name}")

    command = [
        str(editor_path),
        f"/compile:{rel_mq5_path.as_posix()}",
    ]

    logger.info(f"Compiling: {rel_mq5_path}")
    result = subprocess.run(command, cwd=working_dir, capture_output=True, text=True)

    if ea_ex5_path.exists():
        logger.info(f"Compilation succeeded: {ea_ex5_path.name}")
    else:
        logger.error(f"Compilation failed for {ea_mq5_path.name}")
        logger.debug(f"stdout:\n{result.stdout}")
        logger.debug(f"stderr:\n{result.stderr}")


def build_input_lines(data: dict) -> list[str]:
    """ Generate MQL5 `input` variable declarations from YAML input section.

    param data: Parsed indicator data dictionary
    return: List of input declaration strings
    """
    input_lines = []
    for var_name, props in data.get("inputs", {}).items():
        val = props["default"]
        typ = props["type"]

        if isinstance(val, int):
            line = f"input int {var_name} = {val};"

        elif isinstance(val, float):
            line = f"input double {var_name} = {val};"

        else:
            line = f"input {typ} {var_name} = {val};"

        input_lines.append(line)

    return input_lines


def build_enum_definitions(data: dict) -> list[str]:
    """ Generate MQL5 enum definitions from the YAML `enums` section.

    param data: Parsed indicator data dictionary
    return: List of formatted enum definition strings
    """
    enum_definitions = []
    for enum_type, values in data.get("enums", {}).items():
        lines = [f"enum {enum_type} {{"] + [f"    {v}," for v in values] + ["};\n"]
        enum_definitions.append("\n".join(lines))
    return enum_definitions
