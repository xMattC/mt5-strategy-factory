from strategy_factory.stage_execution.stage_config import StageConfig
from strategy_factory.utils import ProjectConfig

from strategy_factory.renderer_tools import build_input_lines
from strategy_factory.renderer_tools import load_results_data
from strategy_factory.stage_execution.stage_config import get_stage_config
from strategy_factory.utils import load_all_pipeline_stages


def render_conformation(project_config: ProjectConfig, stage_config: StageConfig, indi_name: str,
                        indi_data: dict) -> str:
    """Render MQL5 code for the Conformation stage using the provided indicator config.

    Parameters:
    - project_config: Global project settings, including whitelist of symbols.
    - stage_config: Configuration object for the current pipeline stage.
    - indi_name: Name of the indicator being used as the confirmation filter.
    - indi_data: Parsed YAML data for the indicator, including inputs and logic.

    Returns:
    - A rendered MQL5 source code string for use in EA generation.
    """
    stages = load_all_pipeline_stages(project_config.pipeline)

    # Load confirmation indicator data
    conf_logic_inputs = indi_data.get("logic_inputs", {})
    conf_logic_inputs_vars = list(conf_logic_inputs.keys())
    conf_logic_inputs_defaults = [conf_logic_inputs[k]["default"] for k in conf_logic_inputs_vars]
    conf_input_lines = build_input_lines(indi_data)
    conf_buffers = indi_data.get("buffers") or []

    # Load trigger stage result (fixed)
    trigger_stage = get_stage_config(stages, "Trigger")
    trigger_name, trigger_data = load_results_data(project_config.run_name, trigger_stage)

    trigger_logic_inputs = trigger_data.get("logic_inputs", {})
    trigger_logic_inputs_vars = list(trigger_logic_inputs.keys())
    trigger_logic_inputs_defaults = [trigger_logic_inputs[k]["default"] for k in trigger_logic_inputs_vars]

    # Render template
    rendered_ea = stage_config.ea_template.render(
        whitelist=project_config.whitelist,

        # Confirmation indicator
        conf_input_lines=conf_input_lines,
        conf_logic_inputs_vars=conf_logic_inputs_vars,
        conf_logic_inputs_defaults=conf_logic_inputs_defaults,
        conf_custom=indi_data.get("custom"),
        conf_function=indi_data.get("function"),
        conf_path=indi_data.get("indicator_path"),
        conf_inputs_vars=[v["default"] for v in indi_data.get("indicator_inputs", {}).values()],
        conf_buffers=conf_buffers,
        conf_long_conditions=indi_data.get("conf_conditions", {}).get("long"),
        conf_short_conditions=indi_data.get("conf_conditions", {}).get("short"),

        # Trigger indicator (from previous stage)
        trigger_logic_inputs_vars=trigger_logic_inputs_vars,
        trigger_logic_inputs_defaults=trigger_logic_inputs_defaults,
        trigger_custom=trigger_data.get("custom"),
        trigger_function=trigger_data.get("function"),
        trigger_path=trigger_data.get("indicator_path"),
        trigger_inputs_vars=[v["default"] for v in trigger_data.get("indicator_inputs", {}).values()],
        trigger_buffers=trigger_data.get("buffers", []),
        trigger_long_conditions=trigger_data.get("trigger_conditions", {}).get("long"),
        trigger_short_conditions=trigger_data.get("trigger_conditions", {}).get("short"),
    )
    return rendered_ea
