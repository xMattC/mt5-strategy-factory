from pathlib import Path
import yaml


def _load_private_paths() -> dict:
    """Load private MT5 paths from a local YAML config file, and validate them."""
    config_path = Path(__file__).parent.parent.parent / "config" / "local_paths.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Missing config file: {config_path}.")

    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Detect if the user left the template placeholders unchanged
    if "YOUR_USERNAME" in config["mt5_root"] or "YOUR_TERMINAL_ID" in config["mt5_root"]:
        raise ValueError(
            "It looks like you're still using placeholder values in 'config/local_paths.yaml'.\n "
            "Please update the file with your actual MT5 installation paths."
        )

    return config


# Load private path configuration
_private_paths = _load_private_paths()
mt5_root = Path(_private_paths["mt5_root"])
mt5_terminal_exe = Path(_private_paths["mt5_terminal_exe"])
mt5_meta_editor_exe = Path(_private_paths["mt5_meta_editor_exe"])
pro_root = Path(_private_paths["strategy_factory_root"])


def load_paths() -> dict:
    """Return a dictionary of key project paths based on private path config."""

    # Derived paths
    mt5_test_cache = mt5_root / "Tester" / "cache"
    mt5_experts_dir = mt5_root / "MQL5" / "Experts"
    indicator_dir = pro_root / "indicators"
    output_dir = pro_root / "outputs"
    pipelines_dir = pro_root / "strategy_factory" / "pipelines"

    return {
        "MT5_ROOT": mt5_root,
        "MT5_TERM_EXE": mt5_terminal_exe,
        "MT5_EXPERT_DIR": mt5_experts_dir,
        "MT5_META_EDITOR_EXE": mt5_meta_editor_exe,
        "PRO_ROOT": pro_root,
        "MT5_TEST_CACHE": mt5_test_cache,
        "INDICATOR_DIR": indicator_dir,
        "OUTPUT_DIR": output_dir,
        "PIPELINE_DIR": pipelines_dir,
    }
