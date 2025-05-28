from jinja2 import Template

from .common import build_input_lines, flatten_enums


def render_confirmation_ea(template: Template, indicator_name: str, data: dict, trigger_result: dict) -> str:
    """Render MQL5 code for conformation EA stage (2 indicators)."""
    input_lines = list(trigger_result.get("input_lines", [])) + build_input_lines(data)
    enum_definitions = flatten_enums(trigger_result.get("enums")) + flatten_enums(data.get("enums"))
    return template.render(
        indicator_name=indicator_name,
        includes=data.get("includes", []),
        enum_definitions=enum_definitions,
        input_lines=input_lines,
        trigger_path=trigger_result["indicator_path"],
        trigger_inputs=[v["default"] for v in trigger_result["inputs"].values()],
        trigger_buffers=trigger_result.get("buffers", []),
        trigger_long_expr=trigger_result["base_conditions"]["long"],
        trigger_short_expr=trigger_result["base_conditions"]["short"],
        confirmation_path=data["indicator_path"],
        confirmation_inputs=[v["default"] for v in data["inputs"].values()],
        confirmation_buffers=data.get("buffers", []),
        conf_long_expr=data["base_conditions"]["long"],
        conf_short_expr=data["base_conditions"]["short"],
    )
