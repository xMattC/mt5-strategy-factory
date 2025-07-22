import logging
from pathlib import Path

from strategy_factory.stage_execution.stage_config import StageConfig
from strategy_factory.utils import load_paths, ProjectConfig

from .generator_tools import load_indicator_data, load_render_func
from .compiler import compile_ea

logger = logging.getLogger(__name__)


class GenerateEA:
    def __init__(self, project_config: ProjectConfig, stage_config: StageConfig, ea_output_dir: Path):
        """ Initialise the EA generator for a given project and stage configuration.

        param project_config: Project-level configuration object.
        param stage_config: Stage-specific configuration object.
        param ea_output_dir: Directory where the generated EA files should be saved.
        """
        self.project_config = project_config
        self.stage_config = stage_config
        self.ea_output_dir = ea_output_dir
        self.paths = load_paths()
        self.ea_output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> None:
        """ Generate and compile EAs for all indicator YAML files in the stage's indicator directory.

        This method scans the indicator directory defined in the stage configuration and processes
        each `.yaml` file it finds.

        return: None. Logs a warning if no YAML files are found.
        """
        indicator_dir = self._resolve_indicator_dir()
        yaml_files = list(indicator_dir.glob("*.yaml"))
        if not yaml_files:
            logger.warning("No indicator YAML files found in %s", indicator_dir)
            return
        for yaml_file in yaml_files:
            self.generate_one(yaml_file)

    def generate_one(self, yaml_path: Path) -> None:
        """ Generate and compile an EA for a single YAML configuration file.

        This function checks the existence of the input YAML file, generates an MQ5 file,
        and attempts to compile it into an EX5 file. If any stage fails, it logs an error
        and exits early.

        param yaml_path: Path to the YAML config file.
        return: None. Logs errors and stops early if any stage fails.
        """
        if not yaml_path.exists():
            logger.error("YAML file not found: %s", yaml_path)
            return

        mq5_path = self._generate_mq5(yaml_path)
        if not mq5_path.exists():
            logger.warning("Failed to generate .mq5 file for %s", yaml_path.name)
            return

        compile_ea(mq5_path)
        ex5_path = mq5_path.with_suffix(".ex5")
        if not ex5_path.exists():
            logger.warning("Compilation failed for .mq5 file: %s", mq5_path.name)
            return

    def _generate_mq5(self, yaml_path: Path) -> Path:
        """ Render and write the MQ5 source file for a single indicator YAML configuration.

        Uses the render function specified in the stage configuration to convert the
        YAML content into valid MQ5 code and saves it to the output directory.

        param yaml_path: Path to the YAML config file.
        return: Path to the generated `.mq5` source file.
        """
        indicator_name, indicator_data = load_indicator_data(yaml_path)

        render_func = load_render_func(self.stage_config.render_func)
        rendered_ea = render_func(
            project_config=self.project_config,
            stage_config=self.stage_config,
            indi_name=indicator_name,
            indi_data=indicator_data,
        )
        output_file = self.ea_output_dir / f"{yaml_path.stem}.mq5"
        with open(output_file, "w") as f:
            f.write(rendered_ea)

        return output_file

    def _resolve_indicator_dir(self) -> Path:
        """ Resolve the full filesystem path to the indicator directory for this stage.

        The directory is constructed from the global INDICATOR_DIR path joined with
        the stage's `indi_dir` attribute.

        return: Path to the resolved indicator directory.
        raises: ValueError if `indi_dir` is not defined in the stage configuration.
        """
        if not getattr(self.stage_config, "indi_dir", None):
            raise ValueError(f"Stage {self.stage_config.name} must define indi_dir.")

        return self.paths["INDICATOR_DIR"] / self.stage_config.indi_dir
