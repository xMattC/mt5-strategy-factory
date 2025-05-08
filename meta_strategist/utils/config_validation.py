import logging
from datetime import datetime
from dataclasses import asdict

logger = logging.getLogger(__name__)


def check_and_validate_config(config):
    """Run config validation and exit gracefully on failure.

    param config: Configuration dictionary to validate
    """

    try:
        validate_config(asdict(config))
    except ValueError as e:
        print(f"[CONFIG ERROR] {e}")
        exit(1)


def validate_config(config: dict):
    """Validate the structure and values of the run configuration."""

    required_keys = [
        "run_name", "start_date", "end_date", "period", "custom_criteria",
        "symbol_mode", "data_split", "risk", "sl", "tp", "max_iterations"
    ]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: '{key}'")

    # Check date formats
    for date_key in ["start_date", "end_date"]:
        value = config.get(date_key)
        if not value or not isinstance(value, str):
            raise ValueError(f"'{date_key}' must be a non-empty string in YYYY.MM.DD format")
        try:
            datetime.strptime(value, "%Y.%m.%d")
        except ValueError:
            raise ValueError(f"Invalid date format for '{date_key}': must be YYYY.MM.DD")

    # Check numeric types
    for numeric_key in ["risk", "sl", "tp"]:
        if not isinstance(config[numeric_key], (int, float)):
            raise ValueError(f"'{numeric_key}' must be a number")

    if not isinstance(config["max_iterations"], int):
        raise ValueError("'max_iterations' must be an integer")

    # Check enums
    if config["period"] not in {"M1", "M5", "M15", "H1", "H4", "D1"}:
        raise ValueError(f"Invalid period: {config['period']}")

    if config["custom_criteria"] not in {0, 1}:
        raise ValueError("custom_criteria must be 0 or 1")

    if config["data_split"] not in {"none", "year", "month"}:
        raise ValueError("data_split must be one of: none, year, month")

    logger.info("Configuration validated successfully.")
