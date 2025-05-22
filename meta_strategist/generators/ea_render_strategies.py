from jinja2 import Template


def get_render_function(ea_type: str):
    """Return the appropriate rendering function based on the EA type.

    param ea_type: Name of the EA stage/type (must match dictionary keys)
    return: Callable that accepts (template, indicator_name, data) and returns the rendered source code as str
    raises: KeyError if the EA type is unknown
    """
    # Map EA type string to the appropriate render function
    return {
        "Trigger": render_trigger_ea,
        "Conformation": render_confirmation_ea,
        "Volume": render_volume_ea,
        "Exit": render_exit_ea,
        "Trendline": render_baseline_ea,
    }[ea_type]


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


def flatten_enums(enum_obj):
    if not enum_obj:
        return []
    if isinstance(enum_obj, list):
        return enum_obj
    if isinstance(enum_obj, dict):
        # Convert dict to list of MQL5 enum code
        return [f"enum {k} {{ " + ", ".join(v) + " };" for k, v in enum_obj.items()]
    return [str(enum_obj)]


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


def render_volume_ea(template: Template, indicator_name: str, data: dict) -> str:
    """Render EA code for a volume filter stage.

    param template: Jinja2 Template for this EA
    param indicator_name: Name of the EA
    param data: YAML-parsed dictionary, must have trigger/exit info
    return: Rendered MQL5 code as string
    """
    return template.render(
        indicator_name=indicator_name,
        trigger_path=data["trigger_path"],  # Path to the trigger indicator
        exit_path=data["exit_path"],  # Path to the exit/volume indicator
        trigger_inputs=data["trigger_inputs"],  # Trigger indicator input params
        exit_inputs=data["exit_inputs"],  # Exit/volume indicator input params
        logic_settings=data.get("exit_logic", {}),  # Dict of extra logic settings for exit/volume
    )


def render_exit_ea(template: Template, indicator_name: str, data: dict) -> str:
    """Render EA code for an exit stage EA (similar to volume).

    param template: Jinja2 Template for this EA
    param indicator_name: Name of the EA
    param data: YAML-parsed dictionary, must have trigger/exit info
    return: Rendered MQL5 code as string
    """
    return template.render(
        indicator_name=indicator_name,
        trigger_path=data["trigger_path"],
        exit_path=data["exit_path"],
        trigger_inputs=data["trigger_inputs"],
        exit_inputs=data["exit_inputs"],
        logic_settings=data.get("exit_logic", {}),
    )


def render_baseline_ea(template: Template, indicator_name: str, data: dict) -> str:
    """Render EA code for a baseline/trendline stage EA.

    param template: Jinja2 Template for this EA
    param indicator_name: Name of the EA
    param data: YAML-parsed dictionary with multiple indicators and logic
    return: Rendered MQL5 code as string
    """
    return template.render(
        indicator_name=indicator_name,
        indicators=data["indicators"],  # List/dict of all indicators for this baseline EA
        entry_logic=data["entry_logic"],  # Logic for entering trades
        exit_logic=data["exit_logic"]  # Logic for exiting trades
    )


def build_input_lines(data: dict) -> list[str]:
    """ Generate MQL5 `input` variable declarations from YAML input section.

    param data: Parsed indicator data dictionary
    return: List of input declaration strings
    """
    input_lines = []
    # For each input, create a proper MQL5 declaration line
    for var_name, props in data.get("inputs", {}).items():
        val = props["default"]
        typ = props["type"]

        # Choose type-specific formatting
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
    # For each enum type in the config, construct the MQL5 enum block
    for enum_type, values in data.get("enums", {}).items():
        # Each value appears as an enum constant (with indentation)
        lines = [f"enum {enum_type} {{"] + [f"    {v}," for v in values] + ["};\n"]
        enum_definitions.append("\n".join(lines))
    return enum_definitions
