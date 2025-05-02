from dataclasses import dataclass
from pathlib import Path
import configparser
import yaml


@dataclass
class IniConfig:
    output_dir: Path
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
    """Returns a list of all .yaml files in the given indicators directory.

    param indicator_dir: Path to the indicator directory
    return: List of .yaml file Paths
    """
    return list(indicator_dir.glob("*.yaml"))


def generate_all_ini_configs(indicator_dir: Path, expert_dir: Path, config: IniConfig, in_sample: bool):
    """Generate .ini files for all indicators in a directory.

    param indicator_dir: Path to the YAML definitions
    param expert_dir: Path where compiled .ex5 files are located
    param config: IniConfig with shared settings
    param in_sample: Whether this is an in-sample or OOS run
    """
    yaml_paths = get_indicator_yaml_paths(indicator_dir)

    for yaml_path in yaml_paths:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        indicator_name = list(data.keys())[0]
        inputs = data[indicator_name].get("inputs", {})

        expert_path = expert_dir / f"{yaml_path.stem}.mq5"
        if not expert_path.exists():
            print(f"[WARN] Skipping {indicator_name} - no .ex5 file found.")
            continue

        generate_ini_config(config, str(expert_path), in_sample=in_sample, inputs=inputs)


def generate_ini_config(parameters: IniConfig, expert_path: str, in_sample: bool, inputs: dict) -> None:
    """Create an .ini file for MT5 testing or optimization.

    param parameters: Configuration container holding all parameters for .ini generation
    param expert_path: Path to the EA (Expert Advisor) file
    param in_sample: Whether this is an in-sample run (True) or out-of-sample (False)
    """
    indicator_name = Path(expert_path).stem
    sample_type = "IS" if in_sample else "OOS"
    report_name = f"{indicator_name}_{sample_type}"

    cfg = configparser.ConfigParser()
    cfg.optionxform = str

    cfg['Tester'] = {
        "Expert": expert_path,
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
        if key.startswith("inp_"):
            continue

        val = meta['default']

        if in_sample:
            min_v = meta.get('min', val)
            max_v = meta.get('max', val)
            step = meta.get('step', 1)
            cfg['TesterInputs'][key] = f"{val}||{min_v}||{step}||{max_v}||Y"
        else:
            cfg['TesterInputs'][key] = f"{val}||0||0||1||N"

    ini_file_name = parameters.output_dir / f"{indicator_name}_{sample_type}.ini"
    ini_file_name.parent.mkdir(parents=True, exist_ok=True)

    with open(ini_file_name, 'w', encoding='utf-16') as f:
        cfg.write(f)
        print(f"INI file written to: {ini_file_name}")
