from datetime import datetime
from dataclasses import asdict, dataclass
from dataclasses import dataclass, field
import sys
import logging
from pathlib import Path
from pprint import pformat  # Pretty print for dicts/lists

import yaml

from .whitelist_loader import load_whitelist

logger = logging.getLogger(__name__)


@dataclass
class OptSettings:
    opt_criterion: int
    custom_criterion: int
    min_trade: int
    max_iterations: int
    max_iterations_per_param: bool = False


@dataclass
class ProjectConfig:
    run_name: str = "TestRun"
    pipeline: str = "trend_following"
    whitelist_file: str = ""
    whitelist: list[str] = field(default_factory=list)
    start_date: str = ""
    end_date: str = ""
    period: str = "D1"
    main_chart_symbol: str = ""
    deposit: int = 0
    currency: str = "USD"
    leverage: int = 100
    data_split: str = "none"
    risk: float = 0.0
    sl: float = 0.0
    tp: float = 0.0
    opt_settings: dict = field(default_factory=dict)


def load_config_from_yaml(config_path: Path) -> ProjectConfig:
    """ Load a YAML config file and return a Config dataclass instance. Loads whitelist from a separate file specified in
    config, or sets to [Symbol()] if whitelist_file is 'CHART_SYMBOL_ONLY'.

    Exits with an error if the whitelist file does not exist,
    and suggests using 'CHART_SYMBOL_ONLY'.
    """
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)

    # Load opt_settings as before
    opt_data = data.get("opt_settings", {})
    data["opt_settings"] = {k: OptSettings(**v) for k, v in opt_data.items()}

    whitelist_file = data.get("whitelist_file")
    if isinstance(whitelist_file, str) and whitelist_file.upper() == "CHART_SYMBOL_ONLY":
        data["whitelist"] = ["Symbol()"]

    else:
        whitelist_path = Path(whitelist_file)

        if not whitelist_path.exists():
            logger.error(f" Whitelist file not found: {whitelist_path}\nYou may specify 'CHART_SYMBOL_ONLY' in your "
                         f"config to use the current chart symbol instead.")
            sys.exit(1)

        data["whitelist"] = load_whitelist(whitelist_path)

    # --- LOG THE LOADED CONFIG ---
    config = ProjectConfig(**data)
    config_dict = asdict(config)
    config_dict.pop("opt_settings", None)  # Remove opt_settings if present
    logger.info("\nFull config (excluding opt_settings):\n%s", pformat(config_dict, indent=20, width=120))

    return config


def check_and_validate_config(config: ProjectConfig):
    """ Validate the config object, printing and exiting on any error.

    param config: Config instance to validate

    Prints an error and exits if validation fails, so always call this
    before running your main logic.
    """
    try:
        # Convert to dict for easier key-based validation
        validate_config(asdict(config))
    except ValueError as e:
        # Print config errors in a standard format and exit immediately
        print(f"[CONFIG ERROR] {e}")
        exit(1)


# TODO update to a more comprehensive validation.
def validate_config(config: dict):
    """ Validate the structure and values of the run configuration.
    """

    # List all keys that must be present for the config to be valid
    required_keys = [
        "run_name", "start_date", "end_date", "period", "opt_settings",
        "data_split", "risk", "sl", "tp"
    ]

    # Check every required field is in the config
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: '{key}'")

    # --- Date validation ---
    for date_key in ["start_date", "end_date"]:
        value = config.get(date_key)
        if not value or not isinstance(value, str):
            raise ValueError(
                f"'{date_key}' must be a non-empty string in YYYY.MM.DD format"
            )
        try:
            # Parse date to ensure it matches required format
            datetime.strptime(value, "%Y.%m.%d")
        except ValueError:
            raise ValueError(
                f"Invalid date format for '{date_key}': must be YYYY.MM.DD"
            )

    # --- Numeric field validation ---
    for numeric_key in ["risk", "sl", "tp"]:
        if not isinstance(config[numeric_key], (int, float)):
            raise ValueError(f"'{numeric_key}' must be a number")

    # --- Enum / allowed-value validation ---
    allowed_periods = {"M1", "M5", "M15", "H1", "H4", "D1"}
    if config["period"] not in allowed_periods:
        raise ValueError(
            f"Invalid period: {config['period']}. Must be one of: {', '.join(allowed_periods)}"
        )

    allowed_splits = {"none", "year", "month"}
    if config["data_split"] not in allowed_splits:
        raise ValueError(
            "data_split must be one of: none, year, month"
        )

    logger.info("Configuration validated successfully.")
