from jinja2 import Template
from .common import build_input_lines, build_enum_definitions


def render_trigger_ea(template: Template, indicator_name: str, data: dict) -> str:
    """Render EA code for a trigger-only EA.

    param template: Jinja2 Template for this EA
    param indicator_name: Name of the indicator to test as trigger
    param data: Dictionary parsed from YAML config
    return: Rendered MQL5 code as string
    """
    # The most basic single-indicator EA (for trigger tests)
    return template.render(
        indicator_name=indicator_name,
        indicator_path=data["indicator_path"],  # Path to the indicator .ex5 or .mq5
        input_lines=build_input_lines(data),  # MQL5 input variable declarations
        enum_definitions=build_enum_definitions(data),  # MQL5 enum definitions
        inputs=[k for k in data.get("inputs", {})],  # List of input variable names
        buffers=data.get("buffers", []),  # List of buffer indices or names
        base_conditions=data.get("base_conditions", {"long": "false", "short": "false"}),  # Trading conditions
        includes=data.get("includes", [])  # List of MQL5 include files
    )
