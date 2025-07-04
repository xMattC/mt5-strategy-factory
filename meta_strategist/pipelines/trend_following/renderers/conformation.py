from meta_strategist.stage_execution.stage_config import StageConfig
from meta_strategist.utils import ProjectConfig

from meta_strategist.renderer_tools import build_input_lines, build_enum_definitions
from meta_strategist.renderer_tools import load_results_data
from meta_strategist.stage_execution.stage_config import get_stage_config
from meta_strategist.utils import load_all_pipeline_stages


def render_conformation(project_config: ProjectConfig, stage_config: StageConfig, indi_name: str,
                        indi_data: dict) -> str:
    """This render function must accept all standard pipeline arguments—`project_config`, `stage_config`, `indi_name`,
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

    # Extract base conditions for the conformation indicator (long and short)
    conf_long_full = indi_data.get("base_conditions", {}).get("long", "")
    conf_short_full = indi_data.get("base_conditions", {}).get("short", "")

    # Load optimised result for the trigger indicator (from previous pipeline stage)
    stages = load_all_pipeline_stages(project_config.pipeline)
    trigger_stage = get_stage_config(stages, "Trigger")
    trigger_name, trigger_data = load_results_data(project_config.run_name, trigger_stage)

    # Render the EA template, passing all required context variables to the template
    rendered_ea = stage_config.ea_template.render(
        enum_definitions=build_enum_definitions(indi_data, indi_data),
        whitelist=project_config.whitelist,

        # Conformation indicator (to be optimised)
        conf_indicator_name=indi_name,
        conf_input_lines=build_input_lines(indi_data),
        conf_custom=indi_data.get("custom"),  # States if indi is mt5 inbuilt or custom
        conf_function=indi_data.get("function"),  # Only used for mt5 built in indicators
        conf_indicator_path=indi_data.get("indicator_path"),  # Path to indicator .mq5
        conf_inputs_vars=[k for k in indi_data.get("inputs", {})],  # List of input variable names for indicator
        conf_buffers=indi_data.get("buffers", []),  # List of buffer indices or names
        conf_long_conditions=extract_conformation_conditions(conf_long_full),
        conf_short_conditions=extract_conformation_conditions(conf_short_full),

        # Trigger settings (fixed indicator):
        trigger_custom=trigger_data.get("custom"),
        trigger_function=trigger_data.get("function"),
        trigger_path=trigger_data.get("indicator_path"),
        trigger_inputs_vars=[v["default"] for v in trigger_data["inputs"].values()],
        trigger_buffers=trigger_data.get("buffers", []),
        trigger_long_conditions=trigger_data.get("base_conditions", {}).get("long", "false"),
        trigger_short_conditions=trigger_data.get("base_conditions", {}).get("short", "false"),
    )
    return rendered_ea


def extract_conformation_conditions(cond: str) -> str:
    """Extract the part of the condition before '&&' for conformation logic from the indicator in the trigger dir.

    param cond: The full condition string
    return: The condition before '&&', stripped of whitespace
    """
    # Only use the first condition (before the '&&'), or return the whole string if '&&' not present
    return cond.split('&&')[0].strip() if cond else cond
