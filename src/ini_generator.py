from dataclasses import dataclass
from pathlib import Path
import configparser
import yaml

from src.path_config import load_paths
# from src.utils import get_rel_expert_path


@dataclass
class IniConfig:
    # Container for all shared settings used during .ini generation
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
    """Returns a list of all .yaml files in the given indicators' directory.

    param indicator_dir: Path to the indicator directory
    return: List of .yaml file Paths
    """
    return list(indicator_dir.glob("*.yaml"))


def generate_all_ini_configs(expert_dir: Path, config: IniConfig, ini_files_dir: Path,
                             in_sample: bool):
    """Generate .ini files for all indicators in a directory.

    param indicator_dir: Path to the YAML definitions
    param expert_dir: Path where compiled .ex5 files are located
    param config: IniConfig with shared settings
    param in_sample: Whether this is an in-sample or OOS run
    """
    paths = load_paths()
    yaml_paths = get_indicator_yaml_paths(paths["INDICATOR_DIR"])

    for yaml_path in yaml_paths:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        # Extract the top-level indicator name (assumes single-key YAML structure)
        indicator_name = list(data.keys())[0]
        inputs = data[indicator_name].get("inputs", {})

        # Build path to expected compiled EA (.ex5) file
        expert_path = expert_dir / f"{yaml_path.stem}.ex5"
        if not expert_path.exists():
            print(f"[WARN] Skipping {indicator_name} - no .ex5 file found.")
            continue

        # Create the corresponding .ini file
        generate_ini_config(config, str(expert_path), in_sample, ini_files_dir, inputs=inputs)


def generate_ini_config(parameters: IniConfig, expert_path: str, in_sample: bool, ini_files_dir, inputs: dict) -> None:
    """Create an .ini file for MT5 testing or optimization.

    param parameters: Configuration container holding all parameters for .ini generation
    param expert_path: Path to the EA (Expert Advisor) file
    param in_sample: Whether this is an in-sample run (True) or out-of-sample (False)
    """
    indicator_name = Path(expert_path).stem
    sample_type = "IS" if in_sample else "OOS"  # IS = In-sample, OOS = Out-of-sample
    report_name = f"{indicator_name}_{sample_type}"

    # Set up INI file parser
    cfg = configparser.ConfigParser()
    cfg.optionxform = str  # preserve case in keys

    # ----- TESTER SECTION -----
    # Defines the high-level test run parameters for MT5 Strategy Tester
    paths = load_paths()
    expert_rel_path = get_rel_expert_path(Path(expert_path), paths["MT5_EXPERT_DIR"])

    cfg['Tester'] = {
        "Expert": expert_rel_path,
        "Symbol": "EURUSD",  # This could be moved to config or YAML for flexibility
        "Period": parameters.period,
        "Model": "1",  # Every tick
        "FromDate": parameters.start_date,
        "ToDate": parameters.end_date,
        "ForwardMode": "0",
        "Deposit": "100000",
        "Currency": "USD",
        "ProfitInPips": "0",
        "Leverage": "100",
        "ExecutionMode": "0",
        "Optimization": "2",  # Fast genetic algorithm
        "OptimizationCriterion": "6",  # Custom criterion
        "Visual": "0",
        "ReplaceReport": "1",
        "ShutdownTerminal": "1",
        "Report": report_name,
    }

    # ----- TESTER INPUTS -----
    # Defines input parameters and ranges for optimization
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

    # Map for how to encode data split input depending on sample type and config
    split_map = {
        (False, 'year'): '1',
        (True, 'year'): '2',
        (False, 'month'): '3',
        (True, 'month'): '4',
    }
    split_code = split_map.get((in_sample, parameters.data_split), '0')
    cfg['TesterInputs']["inp_data_split_method"] = f"{split_code}||0||0||3||N"

    # Add user-defined inputs from the YAML file (only ones not starting with "inp_")
    for key, meta in inputs.items():
        # if key.startswith("inp_"):
        #     continue  # Reserved or special keys already handled

        val = meta['default']

        if in_sample:
            # Set optimization range for input
            min_v = meta.get('min', val)
            max_v = meta.get('max', val)
            step = meta.get('step', 1)
            cfg['TesterInputs'][key] = f"{val}||{min_v}||{step}||{max_v}||Y"

        else:
            # Fixed value for out-of-sample test. val should come from result of in sample test.
            cfg['TesterInputs'][key] = f"{val}||0||0||1||N"

    # Write .ini file to disk with UTF-16 encoding (required by MT5)
    ini_file_name = ini_files_dir / f"{indicator_name}_{sample_type}.ini"
    ini_file_name.parent.mkdir(parents=True, exist_ok=True)

    with open(ini_file_name, 'w', encoding='utf-16') as f:
        cfg.write(f)
        print(f"INI file written to: {ini_file_name}")


def get_rel_expert_path(absolute_path: Path, mt5_experts_dir: Path) -> str:
    """ Return the relative path of a compiled EA from the MQL5/Experts root, formatted as MT5 expects inside .ini files.

    param absolute_path: Absolute path to the .ex5 EA
    param mt5_experts_dir: Root of MQL5/Experts directory
    return: Relative path string, using forward slashes
    """
    return str(absolute_path.relative_to(mt5_experts_dir))
