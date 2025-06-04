import logging
from pathlib import Path
from ..base import BaseEAGenerator

from jinja2 import Template
from ..ea_utils import build_input_lines, build_enum_definitions, load_indicator_data


logger = logging.getLogger(__name__)


class PreProcTestingEAGenerator(BaseEAGenerator):
    """EA generator for the Trigger stage.

    Implements _generate_mq5() to render the EA source for triggers.
    """

    def _generate_mq5(self, yaml_path: Path) -> Path:
        """Render and write the trigger EA for a single indicator.

        param yaml_path: Path to the indicator YAML
        param indicator_name: The indicator's name
        param data: Parsed YAML config dict for this indicator
        return: Path to written .mq5 file
        """
        # Load optimised result for the trigger indicator (from previous pipeline stage)
        trigger_indi_name, trigger_indi_data = load_indicator_data(yaml_path)
        rendered = render_trigger_ea(self.template, trigger_indi_name, trigger_indi_data)
        output_file = self.ea_dir / f"{yaml_path.stem}.mq5"
        with open(output_file, "w") as f:
            f.write(rendered)
        return output_file


def render_trigger_ea(template: Template, trigger_indi_name: str, trigger_indi_data: dict) -> str:
    """Render EA code for a trigger-only EA.

    param template: Jinja2 Template for this EA
    param indicator_name: Name of the indicator to test as trigger
    param data: Dictionary parsed from YAML config
    return: Rendered MQL5 code as string
    """
    # The most basic single-indicator EA (for trigger tests)
    return template.render(
        enum_definitions=build_enum_definitions(trigger_indi_data),  # MQL5 enum definitions
        trigger_indicator_name=trigger_indi_name,
        trigger_input_lines=build_input_lines(trigger_indi_data),  # MQL5 input variable declarations
        trigger_indicator_path=trigger_indi_data["indicator_path"],  # Path to the indicator .ex5 or .mq5
        trigger_inputs=[k for k in trigger_indi_data.get("inputs", {})],  # List of input variable names
        trigger_buffers=trigger_indi_data.get("buffers", []),  # List of buffer indices or names
        trigger_long_conditions=trigger_indi_data.get("base_conditions", {}).get("long", "false"),
        trigger_short_conditions=trigger_indi_data.get("base_conditions", {}).get("short", "false"),
    )

