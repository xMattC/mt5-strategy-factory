import logging
from pathlib import Path

from .ea_base import BaseEAGenerator
from .ea_render_strategies import render_trigger_ea

logger = logging.getLogger(__name__)


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
