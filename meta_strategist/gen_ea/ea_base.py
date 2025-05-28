import logging
from pathlib import Path
from jinja2 import Template
import yaml

from .ea_compiler import compile_ea
from meta_strategist.pipeline import Stage
from meta_strategist.utils import load_paths

logger = logging.getLogger(__name__)


class BaseEAGenerator:
    """
    Abstract base class for all EA generators.

    All concrete generator subclasses must provide the following public interface:
      - generate_all(): Generate and compile EAs for the relevant indicators.
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



