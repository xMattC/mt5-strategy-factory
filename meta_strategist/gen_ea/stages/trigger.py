import logging
from pathlib import Path
from ..base import BaseEAGenerator
from jinja2 import Template
from ..utils import build_input_lines, build_enum_definitions, load_indicator_data
from meta_strategist.pipeline import Stage

logger = logging.getLogger(__name__)


class TriggerEAGenerator(BaseEAGenerator):
    """EA generator for the Trigger stage.

    Implements _generate_mq5() to render the EA source for triggers.
    """

    def __init__(self, ea_dir: Path, stage: Stage):
        """Initialise the ConformationEAGenerator.

        param ea_dir: Directory where EAs will be output
        param stage: Current pipeline Stage object
        param run_name: Optimisation run name
        """
        super().__init__(ea_dir, stage)

    def _generate_mq5(self, yaml_path: Path) -> Path:
        """Render and write the trigger EA for a single indicator.

        param yaml_path: Path to the indicator YAML
        param indicator_name: The indicator's name
        param data: Parsed YAML config dict for this indicator
        return: Path to written .mq5 file
        """
        # Load trigger indicator (to be optimised in this stage)
        trigger_indi_name, trigger_indi_data = load_indicator_data(yaml_path)

        # Render the EA code using the template and indicator data
        rendered = render_trigger_ea(
            # self.config,
            self.template,
            trigger_indi_name,
            trigger_indi_data
        )

        # Write the rendered EA code to the output .mq5 file
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
    # custom_criterion = config.custom_criteria.get("Trigger")
    # criteria = custom_criterion.criteria
    # min_trades = custom_criterion.min_trade

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
