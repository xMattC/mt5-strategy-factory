from strategy_factory.stage_execution.stage_config import StageConfig
from strategy_factory.utils import ProjectConfig

from strategy_factory.renderer_tools import build_input_lines, build_enum_definitions
from strategy_factory.renderer_tools import load_results_data
from strategy_factory.stage_execution.stage_config import get_stage_config
from strategy_factory.utils import load_all_pipeline_stages


def render_trendline(project_config: ProjectConfig, stage_config: StageConfig, indi_name: str, indi_data: dict) -> str:
    """Render function for the trendline stage.

    Parameters:
    - project_config: ProjectConfig instance for the overall run.
    - stage_config: StageConfig instance for the current pipeline stage.
    - indi_name: Name of the trendline indicator.
    - indi_data: Dictionary parsed from YAML config.

    Returns:
    - Rendered MQL5 code as string.
    """
    stages = load_all_pipeline_stages(project_config.pipeline)

    # Load confirmation stage result
    conformation_stage = get_stage_config(stages, "Conformation")
    conf_name, conf_data = load_results_data(project_config.run_name, conformation_stage)
    conf_logic_inputs = conf_data.get("logic_inputs", {})
    conf_logic_inputs_vars = list(conf_logic_inputs.keys())
    conf_logic_inputs_defaults = [conf_logic_inputs[k]["default"] for k in conf_logic_inputs_vars]

    # Load trigger stage result
    trigger_stage = get_stage_config(stages, "Trigger")
    trigger_name, trigger_data = load_results_data(project_config.run_name, trigger_stage)
    trigger_logic_inputs = trigger_data.get("logic_inputs", {})
    trigger_logic_inputs_vars = list(trigger_logic_inputs.keys())
    trigger_logic_inputs_defaults = [trigger_logic_inputs[k]["default"] for k in trigger_logic_inputs_vars]

    # Extract trendline buffer index
    tl_buff_index = indi_data.get("trendline_buffer_index", {}).get("index")

    rendered_ea = stage_config.ea_template.render(
        whitelist=project_config.whitelist,

        # Trendline indicator
        tl_name=indi_name,
        tl_input_lines=build_input_lines(indi_data),
        tl_custom=indi_data.get("custom"),
        tl_function=indi_data.get("function"),
        tl_path=indi_data.get("indicator_path"),
        tl_inputs_vars=[k for k in indi_data.get("indicator_inputs", {})],
        tl_buffers=indi_data.get("buffers", []),
        tl_buff_index=tl_buff_index,

        # Confirmation indicator
        conf_logic_inputs_vars=conf_logic_inputs_vars,
        conf_logic_inputs_defaults=conf_logic_inputs_defaults,
        conf_custom=conf_data.get("custom"),
        conf_function=conf_data.get("function"),
        conf_path=conf_data.get("indicator_path"),
        conf_inputs_vars=[v["default"] for v in conf_data.get("indicator_inputs", {}).values()],
        conf_buffers=conf_data.get("buffers", []),
        conf_long_conditions=conf_data.get("conf_conditions", {}).get("long"),
        conf_short_conditions=conf_data.get("conf_conditions", {}).get("short"),

        # Trigger indicator
        trigger_logic_inputs_vars=trigger_logic_inputs_vars,
        trigger_logic_inputs_defaults=trigger_logic_inputs_defaults,
        trigger_custom=trigger_data.get("custom"),
        trigger_function=trigger_data.get("function"),
        trigger_path=trigger_data.get("indicator_path"),
        trigger_inputs_vars=[v["default"] for v in trigger_data.get("indicator_inputs", {}).values()],
        trigger_buffers=trigger_data.get("buffers", []),
        trigger_long_conditions=trigger_data.get("trigger_conditions", {}).get("long"),
        trigger_short_conditions=trigger_data.get("trigger_conditions", {}).get("short"),
        trigger_long_agrees_conditions=trigger_data.get("conf_conditions", {}).get("long"),
        trigger_short_agrees_conditions=trigger_data.get("conf_conditions", {}).get("short"),
    )

    return rendered_ea
