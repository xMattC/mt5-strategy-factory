import logging
from pathlib import Path
from meta_strategist.gen_expert_advisor.base import BaseEAGenerator
from meta_strategist.stage_execution import StageConfig

from jinja2 import Template
from meta_strategist.gen_expert_advisor.ea_utils import build_input_lines, build_enum_definitions, load_indicator_data


logger = logging.getLogger(__name__)


class PreProcTestingEAGenerator(BaseEAGenerator):
    """EA generator for the Trigger stage.

    Implements _generate_mq5() to render the EA source for triggers.
    """
    def __init__(self, ea_dir: Path, stage: StageConfig, run_name: str, whitelist: list):
        """Initialise the ConformationEAGenerator.

        param ea_dir: Directory where EAs will be output
        param stage: Current pipeline Stage object
        param run_name: Optimisation run name
        """
        super().__init__(ea_dir, stage, run_name, whitelist)

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
        rendered = render_pre_proc_ea(
            # self.config,
            self.template,
            trigger_indi_name,
            trigger_indi_data,
            symbols_array=self.whitelist
        )

        # Write the rendered EA code to the output .mq5 file
        output_file = self.ea_dir / f"{yaml_path.stem}.mq5"
        with open(output_file, "w") as f:
            f.write(rendered)

        return output_file


def render_pre_proc_ea(template: Template, trigger_indi_name: str, trigger_indi_data: dict, symbols_array: list) -> str:
    """Render EA code for a trigger-only EA.

    param template: Jinja2 Template for this EA
    param indicator_name: Name of the indicator to test as trigger
    param data: Dictionary parsed from YAML config
    return: Rendered MQL5 code as string
    """
    # The most basic single-indicator EA (for trigger tests)
    return template.render(
        enum_definitions=build_enum_definitions(trigger_indi_data),  # MQL5 enum definitions
        symbols_array=symbols_array,

        trigger_indicator_name=trigger_indi_name,
        trigger_input_lines=build_input_lines(trigger_indi_data),  # MQL5 input variable declarations

        trigger_custom=trigger_indi_data.get("custom"),
        trigger_indicator_path=trigger_indi_data.get("indicator_path"),  # Path to the indicator .ex5 or .mq5
        trigger_function=trigger_indi_data.get("function"),

        trigger_inputs=[k for k in trigger_indi_data.get("inputs", {})],  # List of input variable names
        trigger_buffers=trigger_indi_data.get("buffers", []),  # List of buffer indices or names
        trigger_long_conditions=trigger_indi_data.get("base_conditions", {}).get("long", "false"),
        trigger_short_conditions=trigger_indi_data.get("base_conditions", {}).get("short", "false"),
    )

