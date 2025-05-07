import configparser
import logging
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from meta_strategist.generators.ini_opt_param_scale import scale_parameters
from meta_strategist.utils.pathing import load_paths

logger = logging.getLogger(__name__)


@dataclass
class IniConfig:
    """Configuration values used for .ini file generation."""
    run_name: str
    start_date: str
    end_date: str
    period: str
    custom_criteria: str
    symbol_mode: str
    data_split: str
    risk: float
    sl: float
    tp: float
    max_iterations: int


def extract_inputs_from_yaml(yaml_path: Path, expected_key: str) -> dict:
    """Extracts and validates the 'inputs' section from a YAML indicator file.

    param yaml_path: Path to the .yaml file describing the indicator
    param expected_key: Expected top-level key (indicator name) in the YAML
    return: Dictionary of input parameter definitions
    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")

    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    top_key = next(iter(data))
    if top_key.lower() != expected_key.lower():
        logger.warning(f"Top-level key '{top_key}' does not match expected name '{expected_key}'")

    inputs = data[top_key].get("inputs", {})
    if not isinstance(inputs, dict):
        raise ValueError(f"'inputs' section in {yaml_path.name} must be a dictionary")

    return inputs


def create_ini(indi_name: str, expert_dir: Path, config: IniConfig, ini_files_dir: Path,
               in_sample: bool, optimized_parameters: Optional[Dict[str, str]] = None):
    """Generate a .ini file for a given indicator if corresponding .yaml and .ex5 files exist."""
    paths = load_paths()
    yaml_path = paths["INDICATOR_DIR"] / f"{indi_name}.yaml"
    ex5_path = expert_dir / f"{indi_name}.ex5"

    if not yaml_path.exists():
        logger.warning(f"YAML file missing: {yaml_path.name}")
        return None

    if not ex5_path.exists():
        logger.warning(f".ex5 file missing: {ex5_path.name}")
        return None

    # conver yaml input into dict
    try:
        inputs = extract_inputs_from_yaml(yaml_path, indi_name)

    except Exception as e:
        logger.warning(f"Failed to load inputs from YAML: {e}")
        return None

    return _write_ini_file(config, ex5_path, ini_files_dir, inputs, in_sample, optimized_parameters)


def _write_ini_file(config: IniConfig, expert_path: Path, ini_dir: Path, inputs: dict, in_sample: bool,
                    optimized_parameters: Optional[Dict[str, str]]) -> Path:
    """Write a .ini file for MetaTrader 5 backtesting/optimisation."""
    cfg = configparser.ConfigParser()
    cfg.optionxform = str

    indi_name = expert_path.stem
    sample_type = "IS" if in_sample else "OOS"
    report_name = f"{indi_name}_{sample_type}"

    expert_rel_path = get_rel_expert_path(expert_path, load_paths()["MT5_EXPERT_DIR"])

    cfg["Tester"] = _build_tester_section(config, expert_rel_path, report_name)
    cfg["TesterInputs"] = _build_tester_inputs(config, inputs, in_sample, optimized_parameters)

    ini_path = ini_dir / f"{indi_name}_{sample_type}.ini"
    ini_path.parent.mkdir(parents=True, exist_ok=True)

    with open(ini_path, "w", encoding="utf-16") as f:
        cfg.write(f)

    logger.info(f"Generated .ini file: {ini_path}")
    return ini_path


def _build_tester_section(config: IniConfig, expert_path: str, report_name: str) -> dict:
    """Construct the [Tester] section for the .ini file."""
    return {
        "Expert": expert_path,
        "Symbol": "EURUSD",
        "Period": config.period,
        "Model": "1",
        "FromDate": config.start_date,
        "ToDate": config.end_date,
        "ForwardMode": "0",
        "Deposit": "100000",
        "Currency": "USD",
        "ProfitInPips": "0",
        "Leverage": "100",
        "ExecutionMode": "0",
        "Optimization": "2",
        "OptimizationCriterion": "6",
        "Visual": "0",
        "ReplaceReport": "1",
        "ShutdownTerminal": "1",
        "Report": report_name,
    }


def _build_tester_inputs(config: IniConfig, inputs: dict, in_sample: bool,
                         optimized_parameters: Optional[Dict[str, str]]) -> dict:
    """Construct the [TesterInputs] section for the .ini file."""
    tester_inputs = {
        "inp_lot_mode": "2||0||0||2||N",
        "inp_lot_var": f"{config.risk}||2.0||0.2||20||N",
        "inp_sl_mode": "2||0||0||5||N",
        "inp_sl_var": f"{config.sl}||1.0||0.1||10||N",
        "inp_tp_mode": "2||0||0||5||N",
        "inp_tp_var": f"{config.tp}||1.5||0.15||15||N",
        "inp_custom_criteria": f"{config.custom_criteria}||0||0||1||N",
        "inp_sym_mode": f"{config.symbol_mode}||0||0||2||N",
        "inp_force_opt": "1||1||1||2||N" if in_sample else "1||1||1||2||Y",
        "inp_data_split_method": _get_split_code(config.data_split, in_sample),
    }

    scaled_params = scale_parameters(inputs, max_total_iterations=config.max_iterations, mode=0)

    for name, param in scaled_params:
        if optimized_parameters and name.lower() in optimized_parameters:
            value = optimized_parameters[name.lower()]
            tester_inputs[name] = f"{value}||0||0||1||N"
        elif param.get("optimize", True) and in_sample:
            min_val = param.get("min", param["default"])
            max_val = param.get("max", param["default"])
            step = param.get("step", 1)
            tester_inputs[name] = f"{param['default']}||{min_val}||{step}||{max_val}||Y"
        else:
            tester_inputs[name] = f"{param['default']}||0||0||1||N"

    return tester_inputs


def _get_split_code(split_type: str, in_sample: bool) -> str:
    """Return data split code depending on split type and test phase."""
    if split_type == "year":
        split_code = "2" if in_sample else "1"
    elif split_type == "month":
        split_code = "4" if in_sample else "3"
    else:
        split_code = "0"

    return f"{split_code}||0||0||3||N"


def get_rel_expert_path(expert_path: Path, mt5_experts_dir: Path) -> str:
    """Return relative path of expert from MT5 expert directory."""
    return str(expert_path.relative_to(mt5_experts_dir))
