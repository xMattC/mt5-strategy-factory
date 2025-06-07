import logging

from meta_strategist.renderer_tools import build_input_lines, build_enum_definitions
from meta_strategist.stage_execution.stage_config import StageConfig
from meta_strategist.utils import ProjectConfig

logger = logging.getLogger(__name__)


def render_pre_proc_test(project_config: ProjectConfig, stage_config: StageConfig, indi_name: str, indi_data: dict) -> str:
    """ This render function must accept all standard pipeline arguments—`project_config`, `stage_config`, `indi_name`,
    `indi_data`, and `whitelist`—regardless of whether they are all used within the function body.
    This signature is required for compatibility with the EA generation pipeline, which calls all render
    functions with this full set of arguments.

    param project_config: ProjectConfig instance for the overall run
    param stage_config: StageConfig instance for the current pipeline stage
    param indi_name: Name of the indicator to test as trigger
    param indi_data: Dictionary parsed from YAML config
    param whitelist: List of allowed trading symbols
    return: Rendered MQL5 code as string
    """

    # Render the EA template, passing all required context variables to the template
    rendered_ea = stage_config.ea_template.render(
        enum_definitions=build_enum_definitions(indi_data),  # Generate MQL5 enum definitions from YAML
        symbols_array=project_config.whitelist,  # Pass whitelist for symbol iteration in EA

        # Trigger settings (to be optimised):
        trigger_indicator_name=indi_name,  # The name of the indicator being optimised
        trigger_input_lines=build_input_lines(indi_data),  # MQL5 input variable declarations
        trigger_custom=indi_data.get("custom"),  # States if indi is mt5 inbuilt or custom
        trigger_function=indi_data.get("function"),  # Only used for mt5 built in indicators
        trigger_indicator_path=indi_data.get("indicator_path"),  # Path to indicator .mq5
        trigger_inputs=[k for k in indi_data.get("inputs", {})],  # List of input variable names for indicator
        trigger_buffers=indi_data.get("buffers", []),  # List of output buffer indices or names
        trigger_long_conditions=indi_data.get("base_conditions", {}).get("long", "false"),  # Buy logic
        trigger_short_conditions=indi_data.get("base_conditions", {}).get("short", "false"),  # Sell logic
    )
    return rendered_ea
