import configparser
import logging
from pathlib import Path
from typing import Dict, Optional

from meta_strategist.utils import load_paths, Config
from meta_strategist.optimise import Stage

from .extract_inputs import extract_inputs_from_input_yaml
from .scale_parameters import scale_parameters

logger = logging.getLogger(__name__)


def create_ini(indi_name: str, expert_dir: Path, config: Config, ini_files_dir: Path,
               in_sample: bool, stage: Stage, optimized_parameters: Optional[Dict[str, str]] = None, ):
    """Generate a .ini file for a given indicator if corresponding .yaml and .ex5 files exist."""
    paths = load_paths()
    yaml_path = paths["INDICATOR_DIR"] / stage.indi_dir / f"{indi_name}.yaml"
    ex5_path = expert_dir / f"{indi_name}.ex5"

    if not yaml_path.exists():
        logger.warning(f"YAML file missing: {yaml_path.name}")
        return None

    if not ex5_path.exists():
        logger.warning(f".ex5 file missing: {ex5_path.name}")
        return None

    try:
        inputs = extract_inputs_from_input_yaml(yaml_path, indi_name)

    except Exception as e:
        logger.warning(f"Failed to load inputs from YAML: {e}")
        return None

    ini_file_path = _write_ini_file(config, ex5_path, ini_files_dir, inputs, in_sample, stage, optimized_parameters)

    return ini_file_path


def _write_ini_file(config: Config, expert_path: Path, ini_dir: Path, inputs: dict, in_sample: bool, stage: Stage,
                    optimized_parameters: Optional[Dict[str, str]]) -> Path:
    """Write a .ini file for MetaTrader 5 backtesting/optimisation."""
    cfg = configparser.ConfigParser()
    cfg.optionxform = str

    indi_name = expert_path.stem
    sample_type = "IS" if in_sample else "OOS"
    report_name = f"{indi_name}_{sample_type}"

    expert_rel_path = get_rel_expert_path(expert_path, load_paths()["MT5_EXPERT_DIR"])

    cfg["Tester"] = _build_tester_section(config, expert_rel_path, report_name, stage)
    cfg["TesterInputs"] = _build_tester_inputs(config, inputs, in_sample, optimized_parameters, stage)

    ini_file_path = ini_dir / f"{indi_name}_{sample_type}.ini"
    ini_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(ini_file_path, "w", encoding="utf-16") as f:
        cfg.write(f)

    logger.info(f"Generated .ini file: {ini_file_path}")
    return ini_file_path


def _build_tester_section(config: Config, expert_path: str, report_name: str, stage: Stage) -> dict:
    """Construct the [Tester] section for the .ini file."""
    opt_criterion, criteria, min_trade, max_iterations = _get_stage_criteria(config, stage.name)

    return {
        "Expert": expert_path,
        "Symbol": config.main_chart_symbol,
        "Period": config.period,
        "Model": "1",
        "FromDate": config.start_date,
        "ToDate": config.end_date,
        "ForwardMode": "0",
        "Deposit": config.deposit,
        "Currency": config.currency,
        "ProfitInPips": "0",
        "Leverage": config.leverage,
        "ExecutionMode": "0",
        "Optimization": "2",
        "OptimizationCriterion": str(opt_criterion),
        "Visual": "0",
        "ReplaceReport": "1",
        "ShutdownTerminal": "1",
        "Report": report_name,
    }


def _build_tester_inputs(config: Config, inputs: dict, in_sample: bool,
                         optimized_parameters: Optional[Dict[str, str]], stage: Stage) -> dict:
    """Construct the [TesterInputs] section for the .ini file.

    param config: Configuration object with stage-specific custom_criteria dict
    param inputs: Not used here but kept for compatibility
    param in_sample: True if in-sample, else out-of-sample
    param optimized_parameters: Not used here but kept for compatibility
    param stage: String representing current optimisation stage, e.g. "C1", "Exit"
    return: Dictionary of tester input lines for .ini
    """
    # Get the stage-specific custom_criteria, fall back to 0 if not found
    opt_criterion, criteria, min_trade, max_iterations = _get_stage_criteria(config, stage.name)
    tester_inputs = {
        "inp_lot_mode": "2||0||0||2||N",
        "inp_lot_var": f"{config.risk}||2.0||0.2||20||N",
        "inp_sl_mode": "2||0||0||5||N",
        "inp_sl_var": f"{config.sl}||1.0||0.1||10||N",
        "inp_tp_mode": "2||0||0||5||N",
        "inp_tp_var": f"{config.tp}||1.5||0.15||15||N",
        "inp_custom_criteria": f"{criteria}||0||0||1||N",
        "inp_opt_min_trades": f"{min_trade}||0||0||1||N",
        "inp_force_opt": "1||1||1||2||N" if in_sample else "1||1||1||2||Y",
        "inp_data_split_method": _get_split_code(config.data_split, in_sample),
    }

    scaled_params = scale_parameters(inputs, max_total_iterations=max_iterations)

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


def _get_stage_criteria(config, stage_name):
    """
    Return (criteria, min_trade) tuple for the given stage.
    Raises KeyError if the stage is not present.
    """
    crit = config.opt_settings
    if not isinstance(crit, dict):
        raise TypeError("custom_criteria must be a dict of CriterionSettings.")
    try:
        criterion = crit[stage_name]
        return criterion.opt_criterion, criterion.custom_criterion, criterion.min_trade, criterion.max_iterations
    except KeyError:
        raise KeyError(f"custom_criteria not defined for stage '{stage_name}'")


def get_rel_expert_path(expert_path: Path, mt5_experts_dir: Path) -> str:
    """Return relative path of expert from MT5 expert directory."""
    return str(expert_path.relative_to(mt5_experts_dir))
