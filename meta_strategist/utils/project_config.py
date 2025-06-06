import logging
from datetime import datetime
from dataclasses import asdict, dataclass
from typing import Dict
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


@dataclass
class OptSettings:
    """Settings for a single custom criterion.
    """
    opt_criterion: int
    custom_criterion: int
    min_trade: int
    max_iterations: int


@dataclass
class ProjectConfig:
    """Represents all configuration values needed for run file generation.

    Each field corresponds to a user-editable option in the YAML config.
    custom_criteria is a mapping from stage name to CriterionSettings.
    """
    run_name: str
    pipeline: str
    whitelist_file: str
    start_date: str  # Format: YYYY.MM.DD
    end_date: str  # Format: YYYY.MM.DD
    period: str  # Allowed: M1, M5, M15, H1, H4, D1
    main_chart_symbol: str
    deposit: int
    currency: str
    leverage: int
    data_split: str  # Allowed: none, year, month
    risk: float
    sl: float
    tp: float
    opt_settings: Dict[str, OptSettings]  # Per-stage optimisation settings


def load_config_from_yaml(config_path: Path) -> ProjectConfig:
    """Load a YAML config file and return a Config dataclass instance.

    param config_path: Path to the YAML configuration file
    return: Config object populated with data from YAML
    """
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)

    # Convert each custom_criteria entry to CriterionSettings
    opt_data = data.get("opt_settings", {})
    data["opt_settings"] = {k: OptSettings(**v) for k, v in opt_data.items()}

    return ProjectConfig(**data)


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


# TODO update validate config
def validate_config(config: dict):
    """ Validate the structure and values of the run configuration.

    param config: Dict form of the configuration (e.g., asdict(Config))
    raises: ValueError if any validation fails

    Checks for:
        - All required fields present
        - Date format correctness
        - Numeric and enum field correctness
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

    # --- Custom criteria (optional): Check dict or int, and allowed values if desired ---
    # Accept either an int or a dict of ints for custom_criteria
    # custom_criteria = config["custom_criteria"]
    # if isinstance(custom_criteria, dict):
    #     for stage, val in custom_criteria.items():
    #         if not isinstance(val, int):
    #             raise ValueError(f"custom_criteria for stage '{stage}' must be an integer (got {val})")
    # else:
    #     if not isinstance(custom_criteria, int):
    #         raise ValueError(f"custom_criteria must be an integer (got {custom_criteria})")

    logger.info("Configuration validated successfully.")
