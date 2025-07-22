import configparser
import logging
from pathlib import Path
from typing import Dict, Optional

from strategy_factory.utils import load_paths, ProjectConfig
from strategy_factory.stage_execution.stage_config import StageConfig
from .extract_inputs import extract_inputs_from_input_yaml
from .scale_parameters import scale_parameters

logger = logging.getLogger(__name__)


def create_ini(indi_name: str, ea_output_dir: Path, project_config: ProjectConfig, ini_files_dir: Path,
               in_sample: bool, stage_config: StageConfig, optimised_params: Optional[Dict[str, str]] = None):
    """
    Generate a .ini file for a given indicator if the corresponding .yaml and .ex5 files exist.

    param indi_name: Name of the indicator.
    param ea_output_dir: Directory where the .ex5 files are stored.
    param project_config: Project configuration object.
    param ini_files_dir: Directory where the .ini file should be saved.
    param in_sample: True if generating for in-sample testing, else False.
    param stage_config: Stage-specific configuration object.
    param optimised_params: Optional dictionary of parameter overrides.
    return: Path to the generated .ini file, or None if prerequisites are missing.
    """
    paths = load_paths()
    yaml_path = paths["INDICATOR_DIR"] / stage_config.indi_dir / f"{indi_name}.yaml"
    ex5_path = ea_output_dir / f"{indi_name}.ex5"

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

    ini_file_path = _write_ini_file(project_config, ex5_path, ini_files_dir, inputs, in_sample, stage_config,
                                    optimised_params)
    return ini_file_path


def _write_ini_file(project_config: ProjectConfig, expert_path: Path, ini_dir: Path, inputs: dict,
                    in_sample: bool, stage_config: StageConfig,
                    optimised_params: Optional[Dict[str, str]]) -> Path:
    """
    Write a .ini file for MetaTrader 5 backtesting/optimisation.

    param project_config: Project configuration object.
    param expert_path: Path to the compiled .ex5 file.
    param ini_dir: Directory where the .ini file should be saved.
    param inputs: Input parameter dictionary loaded from YAML.
    param in_sample: True if generating for in-sample testing.
    param stage_config: Stage-specific configuration object.
    param optimised_params: Optional dictionary of parameter overrides.
    return: Path to the written .ini file.
    """
    cfg = configparser.ConfigParser()
    cfg.optionxform = str

    indi_name = expert_path.stem
    sample_type = "IS" if in_sample else "OOS"
    report_name = f"{indi_name}_{sample_type}"

    expert_rel_path = get_rel_expert_path(expert_path, load_paths()["MT5_EXPERT_DIR"])

    cfg["Tester"] = _build_tester_section(project_config, expert_rel_path, report_name, stage_config)
    cfg["TesterInputs"] = _build_tester_inputs(project_config, inputs, in_sample, optimised_params, stage_config)

    ini_file_path = ini_dir / f"{indi_name}_{sample_type}.ini"
    ini_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(ini_file_path, "w", encoding="utf-16") as f:
        cfg.write(f)

    logger.info(f"Generated .ini file: {ini_file_path}")
    return ini_file_path


def _build_tester_section(project_config: ProjectConfig, expert_path: str,
                          report_name: str, stage_config: StageConfig) -> dict:
    """
    Construct the [Tester] section for the .ini file.

    param project_config: Project configuration object.
    param expert_path: Relative path to the expert .ex5 file.
    param report_name: Name to be used for the optimisation report.
    param stage_config: Stage-specific configuration object.
    return: Dictionary for the [Tester] section.
    """
    opt_criterion, _, _, _, _ = _get_stage_config_criteria(project_config, stage_config.name)

    return {
        "Expert": expert_path,
        "Symbol": project_config.main_chart_symbol,
        "Period": project_config.period,
        "Model": "1",
        "FromDate": project_config.start_date,
        "ToDate": project_config.end_date,
        "ForwardMode": "0",
        "Deposit": project_config.deposit,
        "Currency": project_config.currency,
        "ProfitInPips": "0",
        "Leverage": project_config.leverage,
        "ExecutionMode": "0",
        "Optimization": "2",
        "OptimizationCriterion": str(opt_criterion),
        "Visual": "0",
        "ReplaceReport": "1",
        "ShutdownTerminal": "1",
        "Report": report_name,
    }


def _build_tester_inputs(project_config: ProjectConfig, inputs: dict, in_sample: bool,
                         optimised_params: Optional[Dict[str, str]],
                         stage_config: StageConfig) -> dict:
    """
    Construct the [TesterInputs] section for the .ini file.

    Combines static inputs (e.g., SL/TP, risk, criteria) and dynamic strategy parameters,
    including parameter scaling and optional override handling.

    param project_config: Project configuration object.
    param inputs: Dictionary of inputs loaded from YAML.
    param in_sample: True if in-sample, else False.
    param optimised_params: Optional dictionary of parameter overrides.
    param stage_config: Stage-specific configuration object.
    return: Dictionary for the [TesterInputs] section.
    """
    _, criteria, min_trade, max_its, max_per_param = _get_stage_config_criteria(project_config, stage_config.name)

    # ---------------------------------------------------------------------
    # STATIC TESTER INPUTS
    tester_inputs = {
        "inp_lot_mode": "2||0||0||2||N",
        "inp_lot_var": f"{project_config.risk}||2.0||0.2||20||N",
        "inp_sl_mode": "2||0||0||5||N",
        "inp_sl_var": f"{project_config.sl}||1.0||0.1||10||N",
        "inp_tp_mode": "2||0||0||5||N",
        "inp_tp_var": f"{project_config.tp}||1.5||0.15||15||N",
        "inp_custom_criteria": f"{criteria}||0||0||1||N",
        "inp_opt_min_trades": f"{min_trade}||0||0||1||N",
        "inp_data_split_method": _get_split_code(project_config.data_split, in_sample),
    }

    # ---------------------------------------------------------------------
    # FORCE OPTIMISATION FLAG
    # - If *none* of the input parameters have optimise=True, we force optimisation.
    # - If out-of-sample (OOS), we must also force optimisation (Y) regardless of input flags.
    # - Otherwise, in-sample with at least one opt param; no need to force optimisation.

    force_optimisation = not any(param.get("optimise", True) for param in inputs.values())

    if force_optimisation or not in_sample:
        tester_inputs["inp_force_opt"] = "1||1||1||2||Y"
    else:
        tester_inputs["inp_force_opt"] = "1||1||1||2||N"

    # ---------------------------------------------------------------------
    # DYNAMIC PARAMETERS (FROM YAML / OVERRIDES)
    scaled_params = scale_parameters(inputs, max_its, max_per_param)
    for name, param in scaled_params:
        name_lc = name.lower()

        if optimised_params and name_lc in optimised_params:
            value = optimised_params[name_lc]
            tester_inputs[name] = f"{value}||0||0||1||N"

        elif param.get("optimise", True) and in_sample:
            min_val = param.get("min", param["default"])
            max_val = param.get("max", param["default"])
            step = param.get("step", 1)
            tester_inputs[name] = f"{param['default']}||{min_val}||{step}||{max_val}||Y"

        else:
            tester_inputs[name] = f"{param['default']}||0||0||1||N"

    return tester_inputs


def _get_split_code(split_type: str, in_sample: bool) -> str:
    """
    Return encoded string for inp_data_split_method.

    param split_type: 'year', 'month', or 'none'.
    param in_sample: Whether the run is in-sample or OOS.
    return: MT5-formatted input string.
    """
    if split_type == "year":
        split_code = "2" if in_sample else "1"
    elif split_type == "month":
        split_code = "4" if in_sample else "3"
    else:
        split_code = "0"

    return f"{split_code}||0||0||3||N"


def _get_stage_config_criteria(project_config, stage_config_name):
    """
    Get optimisation config values for a given stage.

    param project_config: Project config with .opt_settings.
    param stage_config_name: Name of current optimisation stage.
    return: Tuple (opt_criterion, custom_criterion, min_trades, max_iterations, max_per_param).
    """
    opt_settings = project_config.opt_settings

    if not isinstance(opt_settings, dict):
        raise TypeError("project_config.opt_settings must be a dict of CriterionSettings.")

    if stage_config_name not in opt_settings:
        raise KeyError(f"opt_settings not defined for stage_config '{stage_config_name}'")

    s = opt_settings[stage_config_name]
    return s.opt_criterion, s.custom_criterion, s.min_trade, s.max_iterations, s.max_iterations_per_param


def get_rel_expert_path(expert_path: Path, mt5_experts_dir: Path) -> str:
    """
    Return expert path relative to MT5 Expert directory.

    param expert_path: Full .ex5 path.
    param mt5_experts_dir: Root folder for MT5 Experts.
    return: Relative path string for ini [Tester] section.
    """
    return str(expert_path.relative_to(mt5_experts_dir))
