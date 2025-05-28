import logging
from pathlib import Path
from jinja2 import Template
import yaml

from meta_strategist.utils.pathing import load_paths
from meta_strategist.ea.ea_render_strategies import (
    render_trigger_ea,
    render_confirmation_ea,
    # ... add more as needed
)
from meta_strategist.ea.ea_compiler import compile_ea
from meta_strategist.pipeline.stages import Stage
from meta_strategist.utils.pathing import load_paths

logger = logging.getLogger(__name__)


class BaseEAGenerator:
    """Base class for EA generators. Handles all common EA generation and compilation logic for each pipeline stage.

    param ea_dir: Directory where EAs will be written and compiled.
    param stage: The current pipeline Stage object.
    """

    def __init__(self, ea_dir: Path, stage: Stage):
        self.ea_dir = ea_dir                      # Output directory for this stage's EAs
        self.stage = stage                        # Stage object (defines template, etc.)
        self.logger = logger                      # Module-level logger
        self.paths = load_paths()                 # Load project paths from central config
        self.indicator_dir = self.paths["INDICATOR_DIR"]    # Directory with indicator YAMLs
        self.template_path = self.paths["TEMPLATE_DIR"] / stage.template_name    # Path to .mq5 template
        self.template = self._load_template(self.template_path)                  # Load and cache template
        self.ea_dir.mkdir(parents=True, exist_ok=True)                           # Ensure output dir exists

    def generate_all(self) -> None:
        """Generate and compile all EAs for every indicator YAML found for this stage.

        Loops over all .yaml files in the indicator directory. For each file,
        calls the stage-specific EA generator and compiles the result.
        """
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
        """Generate and compile an EA for a single YAML file.

        param yaml_file: Path to the indicator YAML config file
        """
        with open(yaml_file, "r") as f:
            config = yaml.safe_load(f)
        # The indicator name is assumed to be the top-level key in the YAML file
        indicator_name = list(config.keys())[0]
        data = config[indicator_name]
        # Generate the .mq5 file using stage-specific logic
        mq5_path = self._generate_mq5(yaml_file, indicator_name, data)
        # Compile to .ex5 using the MQL5 compiler
        compile_ea(mq5_path)
        self.logger.info(f"Compiled EA successfully: {mq5_path.name}")

    def _generate_mq5(self, yaml_path: Path, indicator_name: str, data: dict) -> Path:
        """Template method to generate the .mq5 EA file for one indicator.

        Should be implemented in each stage-specific subclass.

        param yaml_path: Path to the indicator YAML
        param indicator_name: The indicator's name
        param data: Parsed YAML config dict for this indicator
        return: Path to the written .mq5 file
        """
        raise NotImplementedError

    def _load_template(self, template_path: Path) -> Template:
        """Load and return the Jinja2 template for this stage.

        param template_path: Path to the .mq5 Jinja2 template
        return: Jinja2 Template object
        """
        self.logger.info(f"Loading EA template from: {template_path}")

        with open(template_path, "r") as f:
            return Template(f.read(), trim_blocks=True, lstrip_blocks=True)

    @staticmethod
    def get_compiled_indicators(expert_dir: Path) -> list[str]:
        """Scan a directory for compiled EAs and report missing .ex5 files.

        param expert_dir: Directory containing .mq5/.ex5 files
        return: List of names of compiled indicators (present as both .mq5 and .ex5)
        """
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
        # Write missing EX5s to a text file for debugging
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
    """EA generator for the Trigger stage.

    Implements _generate_mq5() to render the EA source for triggers.
    """

    def _generate_mq5(self, yaml_path: Path, indicator_name: str, data: dict) -> Path:
        """Render and write the trigger EA for a single indicator.

        param yaml_path: Path to the indicator YAML
        param indicator_name: The indicator's name
        param data: Parsed YAML config dict for this indicator
        return: Path to written .mq5 file
        """
        rendered = render_trigger_ea(self.template, indicator_name, data)
        output_file = self.ea_dir / f"{yaml_path.stem}.mq5"
        with open(output_file, "w") as f:
            f.write(rendered)
        return output_file


def load_trigger_data(run_name: str) -> tuple[str, dict]:
    """Load optimised trigger indicator parameters and merge with base YAML.

    This reads the optimised values from the_trigger.yaml for this run,
    merges them into the original indicator YAML structure, and returns both.

    param run_name: Name of the optimisation run (folder in OUTPUT_DIR)
    return: (indicator_name, merged_dict)
    """
    # 1. Read optimised trigger YAML, which should only contain one indicator
    trigger_yaml_path = load_paths()["OUTPUT_DIR"] / run_name / "Trigger" / "the_trigger.yaml"
    with open(trigger_yaml_path, "r") as f:
        trigger_result = yaml.safe_load(f)
    indicator_name = next(iter(trigger_result))
    optimised_params = trigger_result[indicator_name]

    # 2. Load the original YAML for this indicator from INDICATOR_DIR
    indicator_dir = load_paths()["INDICATOR_DIR"]
    base_yaml_path = indicator_dir / f"{indicator_name}.yaml"
    with open(base_yaml_path, "r") as f:
        base = yaml.safe_load(f)
    base_data = base[indicator_name]

    # 3. Overwrite base inputs with optimised defaults, or add them if missing
    for k, v in optimised_params.items():
        if "inputs" in base_data and k in base_data["inputs"]:
            base_data["inputs"][k]["default"] = v
        else:
            # If key is new, add with minimal info; adjust as needed for your schema
            if "inputs" not in base_data:
                base_data["inputs"] = {}
            base_data["inputs"][k] = {"default": v, "type": type(v).__name__}

    return indicator_name, base_data


class ConformationEAGenerator(BaseEAGenerator):
    """EA generator for the Conformation stage.

    param ea_dir: Output directory for EAs
    param stage: The current Stage object
    param run_name: The optimisation run name (used to find trigger output)
    """

    def __init__(self, ea_dir: Path, stage: Stage, run_name: str):
        super().__init__(ea_dir, stage)
        self.run_name = run_name

    def generate_all(self) -> None:
        """Only generate the conformation EA for the single indicator in the_trigger.yaml.

        Looks up the optimised trigger, finds the matching YAML, and processes it.
        """
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
        """Render and write the conformation EA, using trigger-optimised parameters.

        param yaml_path: Path to the indicator YAML
        param indicator_name: The indicator's name
        param data: Parsed YAML config dict for this indicator
        return: Path to written .mq5 file
        """
        trigger_indicator_name, trigger_result = load_trigger_data(self.run_name)
        rendered = render_confirmation_ea(self.template, indicator_name, data, trigger_result)
        output_file = self.ea_dir / f"{yaml_path.stem}.mq5"
        with open(output_file, "w") as f:
            f.write(rendered)
        return output_file


# --- Add other stage-specific generators here as needed ---


def get_ea_generator_for_stage(stage: Stage, ea_dir: Path, run_name: str) -> BaseEAGenerator:
    """Factory function to get the correct EA generator for a given stage.

    param stage: The pipeline stage object
    param ea_dir: Output directory for EAs
    param run_name: The optimisation run name (may be needed for some stages)
    return: Instance of the appropriate BaseEAGenerator subclass
    """
    if stage.name == "Trigger":
        return TriggerEAGenerator(ea_dir, stage)

    elif stage.name == "Conformation":
        assert run_name is not None, "run_name must be provided for Conformation stage"
        return ConformationEAGenerator(ea_dir, stage, run_name)
    # Add other stages as needed
    else:
        raise ValueError(f"No EA generator defined for stage: {stage.name}")

# --- Usage Example (in your pipeline/optimiser) ---

# generator = get_ea_generator_for_stage(stage, expert_dir)
# generator.generate_all()
