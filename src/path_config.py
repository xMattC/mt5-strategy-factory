from pathlib import Path

# Hardcoded root paths
mt5_root = Path(r"C:\Users\mkcor\AppData\Roaming\MetaQuotes\Terminal\49CDDEAA95A409ED22BD2287BB67CB9C")
mt5_terminal_exe = Path(r"C:\Program Files\FTMO MetaTrader 5\terminal64.exe")


def load_paths() -> dict:
    """
    Return a dictionary of key project paths based on hardcoded root inputs.
    Raises FileNotFoundError if any critical path is missing.
    """
    pro_root = mt5_root / "MQL5" / "Experts" / "meta-strategist"

    # Derived paths
    mt5_test_cache = mt5_terminal_exe.parent / "Tester" / "cache"
    mt5_experts_dir = mt5_root / "MQL5" / "Experts"
    template_dir = pro_root / "ea_templates"
    indicator_dir = pro_root / "indicators"

    required = {
        "MT5_ROOT": mt5_root,
        "MT5_TERM_EXE": mt5_terminal_exe,
        "MT5_EXPERT_DIR": mt5_experts_dir,
        "PRO_ROOT": pro_root,
        "MT5_TEST_CACHE": mt5_test_cache,
        "TEMPLATE_DIR": template_dir,
        "INDICATOR_DIR": indicator_dir
    }

    return required
