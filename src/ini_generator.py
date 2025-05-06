import configparser
import logging
import yaml
from dataclasses import dataclass
from pathlib import Path

from src.path_config import load_paths

logger = logging.getLogger(__name__)


@dataclass
class IniConfig:
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


def get_indicator_yaml_paths(indicator_dir: Path) -> list[Path]:
    """Returns a list of all .yaml files in the given indicators' directory."""
    paths = list(indicator_dir.glob("*.yaml"))
    logger.info(f"Found {len(paths)} indicator YAML file(s) in: {indicator_dir}")
    return paths


def generate_all_ini_configs(expert_dir: Path, config: IniConfig, ini_files_dir: Path, in_sample: bool):
    """ Generate .ini files for all indicators in a directory.

    param expert_dir: Path where compiled .ex5 files are located
    param config: IniConfig with shared settings
    param ini_files_dir: Output directory for .ini files
    param in_sample: Whether this is an in-sample or OOS run
    """
    paths = load_paths()
    yaml_paths = get_indicator_yaml_paths(paths["INDICATOR_DIR"])

    if not yaml_paths:
        logger.warning("No YAML files found. Skipping .ini generation.")
        return

    logger.info(f"Generating .ini files in {'IS' if in_sample else 'OOS'} mode...")

    for yaml_path in yaml_paths:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        indicator_name = list(data.keys())[0]
        inputs = data[indicator_name].get("inputs", {})

        expert_path = expert_dir / f"{yaml_path.stem}.ex5"
        if not expert_path.exists():
            logger.warning(f"Skipping {indicator_name} — compiled EA not found at {expert_path}")
            continue

        generate_ini_config(config, str(expert_path), in_sample, ini_files_dir, inputs)


def generate_ini_config(parameters: IniConfig, expert_path: str, in_sample: bool,
                        ini_files_dir: Path, inputs: dict) -> None:
    """ Create an .ini file for MT5 testing or optimization.
    """
    indicator_name = Path(expert_path).stem
    sample_type = "IS" if in_sample else "OOS"
    report_name = f"{indicator_name}_{sample_type}"

    cfg = configparser.ConfigParser()
    cfg.optionxform = str

    paths = load_paths()
    expert_rel_path = get_rel_expert_path(Path(expert_path), paths["MT5_EXPERT_DIR"])

    cfg['Tester'] = {
        "Expert": expert_rel_path,
        "Symbol": "EURUSD",
        "Period": parameters.period,
        "Model": "1",
        "FromDate": parameters.start_date,
        "ToDate": parameters.end_date,
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

    cfg['TesterInputs'] = {
        "inp_lot_mode": "2||0||0||2||N",
        "inp_lot_var": f"{parameters.risk}||2.0||0.2||20||N",
        "inp_sl_mode": "2||0||0||5||N",
        "inp_sl_var": f"{parameters.sl}||1.0||0.1||10||N",
        "inp_tp_mode": "2||0||0||5||N",
        "inp_tp_var": f"{parameters.tp}||1.5||0.15||15||N",
        "inp_custom_criteria": f"{parameters.custom_criteria}||0||0||1||N",
        "inp_sym_mode": f"{parameters.symbol_mode}||0||0||2||N",
        "inp_force_opt": "1||1||1||2||Y",
    }

    split_map = {
        (False, 'year'): '1',
        (True, 'year'): '2',
        (False, 'month'): '3',
        (True, 'month'): '4',
    }
    split_code = split_map.get((in_sample, parameters.data_split), '0')
    cfg['TesterInputs']["inp_data_split_method"] = f"{split_code}||0||0||3||N"

    for key, meta in inputs.items():
        val = meta['default']
        if in_sample:
            min_v = meta.get('min', val)
            max_v = meta.get('max', val)
            step = meta.get('step', 1)
            cfg['TesterInputs'][key] = f"{val}||{min_v}||{step}||{max_v}||Y"
        else:
            cfg['TesterInputs'][key] = f"{val}||0||0||1||N"

    ini_file_name = ini_files_dir / f"{indicator_name}_{sample_type}.ini"
    ini_file_name.parent.mkdir(parents=True, exist_ok=True)

    with open(ini_file_name, 'w', encoding='utf-16') as f:
        cfg.write(f)

    logger.info(f"Generated .ini file: {ini_file_name}")


def get_rel_expert_path(absolute_path: Path, mt5_experts_dir: Path) -> str:
    """Return the relative path of a compiled EA from the MQL5/Experts root, formatted for MT5 .ini usage."""
    return str(absolute_path.relative_to(mt5_experts_dir))
