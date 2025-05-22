
from jinja2 import Template


def render_trigger_ea(template: Template, indicator_name: str, data: dict) -> str:
    return template.render(
        indicator_name=indicator_name,
        indicator_path=data["indicator_path"],
        input_lines=build_input_lines(data),
        enum_definitions=build_enum_definitions(data),
        inputs=[k for k in data.get("inputs", {})],
        buffers=data.get("buffers", []),
        base_conditions=data.get("base_conditions", {"long": "false", "short": "false"}),
        includes=data.get("includes", [])
    )


def render_confirmation_ea(template: Template, indicator_name: str, data: dict) -> str:
    return template.render(
        indicator_name=indicator_name,
        trigger_path=data["trigger_path"],
        confirmation_path=data["confirmation_path"],
        trigger_inputs=data["trigger_inputs"],
        confirmation_inputs=data["confirmation_inputs"],
    )


def render_exit_ea(template: Template, indicator_name: str, data: dict) -> str:
    return template.render(
        indicator_name=indicator_name,
        trigger_path=data["trigger_path"],
        exit_path=data["exit_path"],
        trigger_inputs=data["trigger_inputs"],
        exit_inputs=data["exit_inputs"],
        logic_settings=data.get("exit_logic", {}),
    )


def render_baseline_ea(template: Template, indicator_name: str, data: dict) -> str:
    return template.render(
        indicator_name=indicator_name,
        indicators=data["indicators"],
        entry_logic=data["entry_logic"],
        exit_logic=data["exit_logic"]
    )


def build_input_lines(data: dict) -> list[str]:
    """ Generate MQL5 `input` variable declarations from YAML input section.

    param data: Parsed indicator data dictionary
    return: List of input declaration strings
    """
    input_lines = []
    for var_name, props in data.get("inputs", {}).items():
        val = props["default"]
        typ = props["type"]

        if isinstance(val, int):
            line = f"input int {var_name} = {val};"

        elif isinstance(val, float):
            line = f"input double {var_name} = {val};"

        else:
            line = f"input {typ} {var_name} = {val};"

        input_lines.append(line)

    return input_lines


def build_enum_definitions(data: dict) -> list[str]:
    """ Generate MQL5 enum definitions from the YAML `enums` section.

    param data: Parsed indicator data dictionary
    return: List of formatted enum definition strings
    """
    enum_definitions = []
    for enum_type, values in data.get("enums", {}).items():
        lines = [f"enum {enum_type} {{"] + [f"    {v}," for v in values] + ["};\n"]
        enum_definitions.append("\n".join(lines))
    return enum_definitions
