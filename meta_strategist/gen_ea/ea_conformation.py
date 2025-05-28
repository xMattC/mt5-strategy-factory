import logging
from pathlib import Path

from .ea_render_strategies import render_confirmation_ea
from .ea_base import BaseEAGenerator
from .ea_utils import load_trigger_data
from meta_strategist.pipeline import Stage

logger = logging.getLogger(__name__)


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

