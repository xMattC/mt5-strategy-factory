from strategy_factory.stage_execution.stage_config import StageConfig
from strategy_factory.utils import ProjectConfig

from strategy_factory.renderer_tools import build_input_lines
from strategy_factory.renderer_tools import load_results_data
from strategy_factory.stage_execution.stage_config import get_stage_config
from strategy_factory.utils import load_all_pipeline_stages


def render_volume(project_config: ProjectConfig, stage_config: StageConfig, indi_name: str, indi_data: dict) -> str:
    """Render function for the volume stage.

    Parameters:
    - project_config: ProjectConfig instance for the overall run.
    - stage_config: StageConfig instance for the current pipeline stage.
    - indi_name: Name of the volume indicator.
    - indi_data: Dictionary parsed from YAML config.

    Returns:
    - Rendered MQL5 code as string.
    """
    stages = load_all_pipeline_stages(project_config.pipeline)

    volume_logic_inputs = indi_data.get("logic_inputs") or {}
    volume_logic_inputs_vars = list(volume_logic_inputs.keys())
    volume_logic_inputs_defaults = [volume_logic_inputs[k]["default"] for k in volume_logic_inputs_vars]
    volume_input_lines = build_input_lines(indi_data)
    volume_buffers = indi_data.get("buffers") or []

    # Load other stages
    trendline_stage = get_stage_config(stages, "Trendline")
    tl_name, tl_data = load_results_data(project_config.run_name, trendline_stage)
    tl_logic_inputs = tl_data.get("logic_inputs", {})
    tl_logic_inputs_vars = list(tl_logic_inputs.keys())
    tl_logic_inputs_defaults = [tl_logic_inputs[k]["default"] for k in tl_logic_inputs_vars]

    conformation_stage = get_stage_config(stages, "Conformation")
    conf_name, conf_data = load_results_data(project_config.run_name, conformation_stage)
    conf_logic_inputs = conf_data.get("logic_inputs", {})
    conf_logic_inputs_vars = list(conf_logic_inputs.keys())
    conf_logic_inputs_defaults = [conf_logic_inputs[k]["default"] for k in conf_logic_inputs_vars]

    trigger_stage = get_stage_config(stages, "Trigger")
    trigger_name, trigger_data = load_results_data(project_config.run_name, trigger_stage)
    trigger_logic_inputs = trigger_data.get("logic_inputs", {})
    trigger_logic_inputs_vars = list(trigger_logic_inputs.keys())
    trigger_logic_inputs_defaults = [trigger_logic_inputs[k]["default"] for k in trigger_logic_inputs_vars]

    rendered_ea = stage_config.ea_template.render(
        whitelist=project_config.whitelist,

        # Volume indicator
        volume_indicator_input_lines=volume_input_lines,
        volume_logic_inputs_vars=volume_logic_inputs_vars,
        volume_logic_inputs_defaults=volume_logic_inputs_defaults,
        volume_custom=indi_data.get("custom"),
        volume_function=indi_data.get("function"),
        volume_indicator_path=indi_data.get("indicator_path"),
        volume_inputs_vars=[v["default"] for v in indi_data["indicator_inputs"].values()],
        volume_buffers=volume_buffers,
        volume_long_conditions=indi_data.get("volume_conditions", {}).get("long"),
        volume_short_conditions=indi_data.get("volume_conditions", {}).get("short"),

        # Trendline indicator
        tl_name=tl_name,
        tl_input_lines=build_input_lines(tl_data),
        tl_logic_inputs_vars=tl_logic_inputs_vars,
        tl_logic_inputs_defaults=tl_logic_inputs_defaults,
        tl_custom=tl_data.get("custom"),
        tl_function=tl_data.get("function"),
        tl_indicator_path=tl_data.get("indicator_path"),
        tl_inputs_vars=[v["default"] for v in tl_data["indicator_inputs"].values()],
        tl_buffers=tl_data.get("buffers", []),
        trendline_buffer_index=tl_data.get("trendline_buffer_index", {}).get("index"),

        # Confirmation
        conf_logic_inputs_vars=conf_logic_inputs_vars,
        conf_logic_inputs_defaults=conf_logic_inputs_defaults,
        conf_custom=conf_data.get("custom"),
        conf_function=conf_data.get("function"),
        conf_indicator_path=conf_data.get("indicator_path"),
        conf_inputs_vars=[v["default"] for v in conf_data["indicator_inputs"].values()],
        conf_buffers=conf_data.get("buffers", []),
        conf_long_conditions=conf_data.get("conf_conditions", {}).get("long"),
        conf_short_conditions=conf_data.get("conf_conditions", {}).get("short"),

        # Trigger
        trigger_logic_inputs_vars=trigger_logic_inputs_vars,
        trigger_logic_inputs_defaults=trigger_logic_inputs_defaults,
        trigger_custom=trigger_data.get("custom"),
        trigger_function=trigger_data.get("function"),
        trigger_path=trigger_data.get("indicator_path"),
        trigger_inputs_vars=[v["default"] for v in trigger_data["indicator_inputs"].values()],
        trigger_buffers=trigger_data.get("buffers", []),
        trigger_long_conditions=trigger_data.get("trigger_conditions", {}).get("long"),
        trigger_short_conditions=trigger_data.get("trigger_conditions", {}).get("short"),
        trigger_long_agrees_conditions=trigger_data.get("conf_conditions", {}).get("long"),
        trigger_short_agrees_conditions=trigger_data.get("conf_conditions", {}).get("short"),
    )

    return rendered_ea
