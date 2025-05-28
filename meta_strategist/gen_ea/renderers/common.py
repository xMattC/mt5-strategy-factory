def flatten_enums(enum_obj):
    if not enum_obj:
        return []
    if isinstance(enum_obj, list):
        return enum_obj
    if isinstance(enum_obj, dict):
        # Convert dict to list of MQL5 enum code
        return [f"enum {k} {{ " + ", ".join(v) + " };" for k, v in enum_obj.items()]
    return [str(enum_obj)]


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
