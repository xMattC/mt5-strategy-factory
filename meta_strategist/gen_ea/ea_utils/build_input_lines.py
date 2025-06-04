
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
