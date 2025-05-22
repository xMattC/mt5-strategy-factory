import logging
import subprocess
from pathlib import Path

import yaml
from jinja2 import Template

from meta_strategist.utils.pathing import load_paths
from meta_strategist.generators.ea_render_strategies import (render_trigger_ea, render_confirmation_ea, render_exit_ea,
                                                             render_baseline_ea)

logger = logging.getLogger(__name__)

__all__ = ["generate_all_eas", "get_compiled_indicators"]


def generate_all_eas(ea_dir: Path, ea_template_path: Path, ea_type: str) -> None:
    """ Orchestrates EA generation and compilation for all indicator YAMLs.

    param ea_dir: Directory where generated .mq5 files will be saved
    param ea_template_path: Path to the Jinja2 EA template file
    param ea_type: Type of EA being generated (e.g. 'trigger', 'confirmation')
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
            process_single_ea(yaml_file, template, ea_dir, terminal_path, ea_type)
        except Exception as e:
            logger.error(f"Error processing {yaml_file.name}: {e}")


def get_compiled_indicators(expert_dir: Path) -> list[str]:
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

    if un_compiled:
        report_path = expert_dir / "00_un_compiled.txt"
        with open(report_path, "w") as f:
            f.write("Indicators with missing .ex5:\n")
            f.writelines(f"- {name}\n" for name in sorted(un_compiled))
        logger.info(f"Wrote un-compiled list to: {report_path}")

    if not compiled_indicators:
        logger.info("No compiled indicators (.ex5) found.")
    else:
        logger.info(f"Found {len(compiled_indicators)} compiled indicators.")

    return compiled_indicators


def load_template(template_path: Path) -> Template:
    logger.info(f"Loading EA template from: {template_path}")
    try:
        with open(template_path, "r") as f:
            return Template(f.read(), trim_blocks=True, lstrip_blocks=True)
    except Exception as e:
        logger.error(f"Failed to load EA template: {template_path}")
        raise


def process_single_ea(yaml_file: Path, template: Template, ea_dir: Path,
                      terminal_path: Path, ea_type: str) -> None:
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)

    indicator_name = list(config.keys())[0]
    data = config[indicator_name]

    mq5_path = generate_ea_mq5(yaml_file, template, indicator_name, data, ea_dir, ea_type)
    compile_ea(mq5_path)
    logger.info(f"Compiled EA successfully: {mq5_path.name}")


def generate_ea_mq5(yaml_path: Path, template: Template, indicator_name: str,
                    data: dict, ea_dir: Path, ea_type: str = "trigger") -> Path:
    logger.debug(f"Generating EA of type '{ea_type}' for: {indicator_name}")

    render_function = {
        "trigger": render_trigger_ea,
        "confirmation": render_confirmation_ea,
        "exit": render_exit_ea,
        "baseline": render_baseline_ea,
    }.get(ea_type)

    if render_function is None:
        raise ValueError(f"Unsupported EA type: {ea_type}")

    rendered = render_function(template, indicator_name, data)

    suffix = {
        "trigger": "",
        "confirmation": "_CONF",
        "exit": "_EXIT",
        "baseline": "_BASE",
    }.get(ea_type, "")

    output_file = ea_dir / f"{yaml_path.stem}{suffix}.mq5"
    with open(output_file, "w") as f:
        f.write(rendered)

    logger.info(f"Generated EA: {output_file}")
    return output_file


def compile_ea(ea_mq5_path: Path) -> None:
    if not ea_mq5_path.exists():
        raise FileNotFoundError(f".mq5 file not found: {ea_mq5_path}")

    paths = load_paths()
    editor_path = paths["MT5_META_EDITOR_EXE"]
    if not editor_path.exists():
        raise FileNotFoundError(f"MetaEditor not found at: {editor_path}")

    rel_mq5_path = ea_mq5_path.relative_to(ea_mq5_path.parents[ea_mq5_path.parts.index("MQL5")])
    working_dir = ea_mq5_path.parents[ea_mq5_path.parts.index("MQL5")]
    ea_ex5_path = ea_mq5_path.with_suffix(".ex5")

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
