import logging
from pathlib import Path
from jinja2 import Template

from meta_strategist.pipeline import Stage
from meta_strategist.utils import load_paths, Config

from .compiler import compile_ea


class BaseEAGenerator:
    """Abstract base class for all EA generators.

    All concrete subclasses must implement _generate_mq5().
    Public interface:
        - generate_all(): Process all YAMLs in indicator_dir.
        - generate_one(yaml_path): Process a single YAML.
    """

    def __init__(self, ea_dir: Path, stage: Stage):
        self.ea_dir = ea_dir
        self.stage = stage
        self.logger = logging.getLogger(self.__class__.__name__)
        self.paths = load_paths()
        self.indicator_dir = self._resolve_indicator_dir()
        self.template_path = self.paths["TEMPLATE_DIR"] / self.stage.template_name
        self.template = self._load_template()
        self.ea_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> None:
        """Generate and compile all EAs for every indicator YAML found for this stage."""
        yaml_files = list(self.indicator_dir.glob("*.yaml"))
        if not yaml_files:
            self.logger.warning("No indicator YAML files found in %s", self.indicator_dir)
            return
        for yaml_file in yaml_files:
            self.generate_one(yaml_file)

    def generate_one(self, yaml_path: Path) -> None:
        """Generate and compile an EA for a single YAML file.

        param yaml_path: Path to the indicator YAML config file
        """
        if not yaml_path.exists():
            self.logger.error("YAML file not found: %s", yaml_path)
            return
        try:
            self._process_single(yaml_path)
            self.logger.info("Successfully generated and compiled EA for %s", yaml_path.name)
        except Exception as e:
            self.logger.error("Error processing %s: %s", yaml_path.name, e)

    def _process_single(self, yaml_file: Path) -> None:
        """Generate and compile an EA for a single YAML file."""
        mq5_path = self._generate_mq5(yaml_file)
        compile_ea(mq5_path)
        self.logger.info("Compiled EA successfully: %s", mq5_path.name)

    def _generate_mq5(self, yaml_path: Path) -> Path:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    def _load_template(self) -> Template:
        """ Load Jinja2 template for this stage."""
        self.logger.info("Loading EA template from: %s", self.template_path)
        with open(self.template_path, "r") as f:
            self.template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)
        return self.template

    def _resolve_indicator_dir(self) -> Path:
        """Resolve the full path to the indicator directory for this stage."""
        if not getattr(self.stage, "indi_dir", None):
            raise ValueError(f"Stage {self.stage.name} must define indi_dir.")
        return self.paths["INDICATOR_DIR"] / self.stage.indi_dir
