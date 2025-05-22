import logging
from pathlib import Path
from jinja2 import Template
import yaml

from meta_strategist.utils.pathing import load_paths
from meta_strategist.generators.ea_render_strategies import (
    render_trigger_ea,
    render_confirmation_ea,
    # ... add more as needed
)
from meta_strategist.generators.ea_compiler import compile_ea
from meta_strategist.pipeline.stages import Stage
from meta_strategist.utils.pathing import load_paths

logger = logging.getLogger(__name__)


class BaseEAGenerator:
    """Base class for EA generators, handles common logic for all stages."""

    def __init__(self, ea_dir: Path, stage: Stage):
        self.ea_dir = ea_dir
        self.stage = stage
        self.logger = logger
        self.paths = load_paths()
        self.indicator_dir = self.paths["INDICATOR_DIR"]
        self.template_path = self.paths["TEMPLATE_DIR"] / stage.template_name
        self.template = self._load_template(self.template_path)
        self.ea_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> None:
        """Generate and compile all EAs for each indicator YAML for the current stage."""
        yaml_files = list(self.indicator_dir.glob("*.yaml"))
        if not yaml_files:
            self.logger.warning("No indicator YAML files found.")
            return
        for yaml_file in yaml_files:
            try:
                self._process_single(yaml_file)
            except Exception as e:
                self.logger.error(f"Error processing {yaml_file.name}: {e}")

    def _process_single(self, yaml_file: Path) -> None:
        """Generate and compile an EA from a single YAML config."""
        with open(yaml_file, "r") as f:
            config = yaml.safe_load(f)
        indicator_name = list(config.keys())[0]
        data = config[indicator_name]
        mq5_path = self._generate_mq5(yaml_file, indicator_name, data)
        compile_ea(mq5_path)
        self.logger.info(f"Compiled EA successfully: {mq5_path.name}")

    def _generate_mq5(self, yaml_path: Path, indicator_name: str, data: dict) -> Path:
        """Override in subclasses for custom rendering logic."""
        raise NotImplementedError

    def _load_template(self, template_path: Path) -> Template:
        self.logger.info(f"Loading EA template from: {template_path}")
        with open(template_path, "r") as f:
            return Template(f.read(), trim_blocks=True, lstrip_blocks=True)

    @staticmethod
    def get_compiled_indicators(expert_dir: Path) -> list[str]:
        """Scan a directory and return compiled EA names; log uncompiled ones."""
        _logger = logging.getLogger(__name__)
        compiled_indicators = []
        un_compiled = []
        mq5_files = list(expert_dir.glob("*.mq5"))
        ex5_files = {f.stem for f in expert_dir.glob("*.ex5")}
        for mq5_file in mq5_files:
            base_name = mq5_file.stem
            if base_name in ex5_files:
                compiled_indicators.append(base_name)
            else:
                _logger.warning(f"MQ5 exists but EX5 missing for: {base_name}")
                un_compiled.append(base_name)
        if un_compiled:
            report_path = expert_dir / "00_un_compiled.txt"
            with open(report_path, "w") as f:
                f.write("Indicators with missing .ex5:\n")
                f.writelines(f"- {name}\n" for name in sorted(un_compiled))
            _logger.info(f"Wrote un-compiled list to: {report_path}")
        if not compiled_indicators:
            _logger.info("No compiled indicators (.ex5) found.")
        else:
            _logger.info(f"Found {len(compiled_indicators)} compiled indicators.")
        return compiled_indicators


# --- Stage-Specific Generator Subclasses ---

class TriggerEAGenerator(BaseEAGenerator):
    """EA generator for Trigger stage."""

    def _generate_mq5(self, yaml_path: Path, indicator_name: str, data: dict) -> Path:
        rendered = render_trigger_ea(self.template, indicator_name, data)
        output_file = self.ea_dir / f"{yaml_path.stem}.mq5"
        with open(output_file, "w") as f:
            f.write(rendered)
        return output_file


def load_trigger_data(run_name: str) -> tuple[str, dict]:
    """
    Loads optimised trigger info from the_trigger.yaml and merges with the original YAML.
    return: (indicator_name, merged_dict)
    """
    # 1. Read the_trigger.yaml (should only have one indicator)
    trigger_yaml_path = load_paths()["OUTPUT_DIR"] / run_name / "Trigger" / "the_trigger.yaml"
    with open(trigger_yaml_path, "r") as f:
        trigger_result = yaml.safe_load(f)
    indicator_name = next(iter(trigger_result))
    optimised_params = trigger_result[indicator_name]

    # 2. Read original indicator YAML
    indicator_dir = load_paths()["INDICATOR_DIR"]
    base_yaml_path = indicator_dir / f"{indicator_name}.yaml"
    with open(base_yaml_path, "r") as f:
        base = yaml.safe_load(f)
    base_data = base[indicator_name]

    # 3. Update original YAML's inputs with optimised values
    for k, v in optimised_params.items():
        if "inputs" in base_data and k in base_data["inputs"]:
            base_data["inputs"][k]["default"] = v
        else:
            # If key wasn't present, create it as a basic int/float (you can adjust this logic)
            if "inputs" not in base_data:
                base_data["inputs"] = {}
            base_data["inputs"][k] = {"default": v, "type": type(v).__name__}

    return indicator_name, base_data


class ConformationEAGenerator(BaseEAGenerator):
    def __init__(self, ea_dir: Path, stage: Stage, run_name: str):
        super().__init__(ea_dir, stage)
        self.run_name = run_name

    def generate_all(self) -> None:
        # Only generate for the indicator in the_trigger.yaml
        trigger_indicator_name, trigger_result = load_trigger_data(self.run_name)
        yaml_file = self.indicator_dir / f"{trigger_indicator_name}.yaml"
        if not yaml_file.exists():
            self.logger.error(f"Indicator YAML '{yaml_file}' not found for Conformation generation.")
            return
        try:
            self._process_single(yaml_file)
        except Exception as e:
            self.logger.error(f"Error processing {yaml_file.name}: {e}")

    def _generate_mq5(self, yaml_path: Path, indicator_name: str, data: dict) -> Path:
        trigger_indicator_name, trigger_result = load_trigger_data(self.run_name)
        rendered = render_confirmation_ea(self.template, indicator_name, data, trigger_result)
        output_file = self.ea_dir / f"{yaml_path.stem}.mq5"
        with open(output_file, "w") as f:
            f.write(rendered)
        return output_file


# --- Add other stage-specific generators here as needed ---

# --- Factory Function ---

def get_ea_generator_for_stage(stage: Stage, ea_dir: Path, run_name: str) -> BaseEAGenerator:
    if stage.name == "Trigger":
        return TriggerEAGenerator(ea_dir, stage)
    elif stage.name == "Conformation":
        assert run_name is not None, "run_name must be provided for Conformation stage"
        return ConformationEAGenerator(ea_dir, stage, run_name)
    # Add other stages...
    else:
        raise ValueError(f"No EA generator defined for stage: {stage.name}")

# --- Usage Example (in your pipeline/optimiser) ---

# generator = get_ea_generator_for_stage(stage, expert_dir)
# generator.generate_all()
