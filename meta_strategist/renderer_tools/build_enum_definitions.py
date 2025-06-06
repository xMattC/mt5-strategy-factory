def build_enum_definitions(*data_sets: dict) -> list[str]:
    """Generate MQL5 enum definitions from multiple YAML `enums` sections.

    param data_sets: One or more parsed indicator data dictionaries
    return: List of formatted enum definition strings (unique enum types only)
    """
    enum_blocks = {}
    for data in data_sets:
        for enum_type, values in data.get("enums", {}).items():
            # Prefer the first occurrence if enums overlap; adjust logic if you want to merge or overwrite
            if enum_type not in enum_blocks:
                lines = [f"enum {enum_type} {{"] + [f"    {v}," for v in values] + ["};\n"]
                enum_blocks[enum_type] = "\n".join(lines)
    return list(enum_blocks.values())
