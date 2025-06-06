import logging
from pathlib import Path

from meta_strategist.stage_execution.stage_config import StageConfig
from meta_strategist.utils import load_paths, ProjectConfig

from .generator_tools import load_indicator_data, load_template, load_render_func
from .compiler import compile_ea


class GenerateEA:
    """Generic EA generator."""

    def __init__(self, project_config: ProjectConfig, stage_config: StageConfig, ea_output_dir: Path, whitelist: list):
        self.project_config = project_config
        self.stage_config = stage_config
        self.ea_output_dir = ea_output_dir
        self.whitelist = whitelist
        self.logger = logging.getLogger(self.__class__.__name__)
        self.paths = load_paths()
        self.indicator_dir = self._resolve_indicator_dir()
        self.render_func = load_render_func(stage_config.render_func)
        self.ea_output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> None:
        """Generate and compile all EAs for every indicator YAML found in stage_config indi dir."""
        yaml_files = list(self.indicator_dir.glob("*.yaml"))
        if not yaml_files:
            self.logger.warning("No indicator YAML files found in %s", self.indicator_dir)
            return
        for yaml_file in yaml_files:
            self.generate_one(yaml_file)

    def generate_one(self, yaml_path: Path) -> None:
        """Generate and compile an EA for a single YAML file."""
        if not yaml_path.exists():
            self.logger.error("YAML file not found: %s", yaml_path)
            return
        try:
            mq5_path = self._generate_mq5(yaml_path)
            compile_ea(mq5_path)
            self.logger.info("Successfully generated and compiled EA for %s", yaml_path.name)
        except Exception as e:
            self.logger.error("Error processing %s: %s", yaml_path.name, e)

    def _generate_mq5(self, yaml_path: Path) -> Path:
        """Render and write the EA for a single indicator using the pipeline's render function."""
        indi_name, indi_data = load_indicator_data(yaml_path)

        rendered = self.render_func(
            self.project_config,
            self.stage_config,
            indi_name,
            indi_data,
            symbols_array=self.whitelist
        )
        output_file = self.ea_output_dir / f"{yaml_path.stem}.mq5"
        with open(output_file, "w") as f:
            f.write(rendered)
        return output_file

    def _resolve_indicator_dir(self) -> Path:
        """Resolve the full path to the indicator directory for this stage_config."""
        if not getattr(self.stage_config, "indi_dir", None):
            raise ValueError(f"Stage {self.stage_config.name} must define indi_dir.")
        return self.paths["INDICATOR_DIR"] / self.stage_config.indi_dir
