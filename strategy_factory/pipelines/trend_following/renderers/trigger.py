import logging

from strategy_factory.renderer_tools import build_input_lines, build_enum_definitions
from strategy_factory.stage_execution.stage_config import StageConfig
from strategy_factory.utils import ProjectConfig

logger = logging.getLogger(__name__)


def render_trigger(project_config: ProjectConfig, stage_config: StageConfig, indi_name: str, indi_data: dict) -> str:
    """Render MQL5 code for the Trigger stage using the provided indicator config.

    Parameters:
    - project_config: Global project settings, including whitelist of symbols.
    - stage_config: Configuration object for the current pipeline stage.
    - indi_name: Name of the indicator being used as the trigger.
    - indi_data: Parsed YAML data for the indicator, including inputs and logic.

    Returns:
    - A rendered MQL5 source code string for use in EA generation.
    """
    trigger_logic_inputs = indi_data.get("logic_inputs") or {}
    trigger_logic_inputs_vars = list(trigger_logic_inputs.keys())
    trigger_logic_inputs_defaults = [trigger_logic_inputs[k]["default"] for k in trigger_logic_inputs_vars]

    # Render the EA template, passing all required context variables to the template
    rendered_ea = stage_config.ea_template.render(
        symbols_array=project_config.whitelist,  # Pass whitelist for symbol iteration in EA

        # Trigger settings (to be optimised):
        trigger_indicator_name=indi_name,  # The name of the indicator being optimised
        trigger_input_lines=build_input_lines(indi_data),  # MQL5 input variable declarations
        trigger_logic_inputs_vars=trigger_logic_inputs_vars,
        trigger_logic_inputs_defaults=trigger_logic_inputs_defaults,
        trigger_custom=indi_data.get("custom"),  # States if indi is mt5 inbuilt or custom
        trigger_function=indi_data.get("function"),  # Only used for mt5 built in indicators
        trigger_path=indi_data.get("indicator_path"),  # Path to indicator .mq5
        trigger_inputs=[k for k in indi_data.get("indicator_inputs", {})],  # List of input variable names for indicator
        trigger_buffers=indi_data.get("buffers", []),  # List of output buffer indices or names
        trigger_long_conditions=indi_data.get("trigger_conditions", {}).get("long"),
        trigger_short_conditions=indi_data.get("trigger_conditions", {}).get("short"),
    )
    return rendered_ea
