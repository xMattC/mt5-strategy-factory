from pathlib import Path
import configparser


def generate_ini_config(expert_path: str, output_path: Path, start_date: str, end_date: str, period: str,
                        custom_criteria: str, symbol_mode: str, data_split: str, risk: float, sl: float, tp: float,
                        report_name: str, inputs: dict, is_out_sample: bool = False, opt_results: dict = None):
    """Create an .ini file for MT5 testing or optimization.

    Parameters:
    expert_path: relative path to the EA
    output_path: full path to output .ini
    start_date, end_date: date strings YYYY.MM.DD
    period: MT5 period (e.g. Daily, H1)
    custom_criteria: str, code for custom loss function
    symbol_mode: str, EA input symbol selection mode
    data_split: 'year' or 'month'
    risk, sl, tp: floats for lot size, SL, TP
    report_name: name of the report file
    inputs: dict of parameter defaults and optimization flags
    is_out_sample: if generating OOS test
    opt_results: if OOS, fixed values from optimization results
    """
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg['Tester'] = {
        "Expert": expert_path,
        "Symbol": "EURUSD",
        "Period": period,
        "Model": "1",
        "FromDate": start_date,
        "ToDate": end_date,
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
        "inp_lot_var": f"{risk}||2.0||0.2||20||N",
        "inp_sl_mode": "2||0||0||5||N",
        "inp_sl_var": f"{sl}||1.0||0.1||10||N",
        "inp_tp_mode": "2||0||0||5||N",
        "inp_tp_var": f"{tp}||1.5||0.15||15||N",
        "inp_custom_criteria": f"{custom_criteria}||0||0||1||N",
        "inp_sym_mode": f"{symbol_mode}||0||0||2||N",
        "inp_force_opt": "1||1||1||2||Y",
    }

    split_map = {
        (False, 'year'): '1',
        (False, 'month'): '3',
        (True, 'year'): '2',
        (True, 'month'): '4',
    }
    split_code = split_map.get((is_out_sample, data_split), '0')
    cfg['TesterInputs']["inp_data_split_method"] = f"{split_code}||0||0||3||N"

    for key, meta in inputs.items():

        if key.startswith("inp_"):  # already included above
            continue

        val = meta['default']

        if is_out_sample and opt_results and key in opt_results:
            val = opt_results[key]
            cfg['TesterInputs'][key] = f"{val}||0||0||1||N"

        elif meta.get('optimize', False):
            min_v = meta.get('min', val)
            max_v = meta.get('max', val)
            step = meta.get('step', 1)
            cfg['TesterInputs'][key] = f"{val}||{min_v}||{step}||{max_v}||Y"

        else:
            cfg['TesterInputs'][key] = f"{val}||0||0||1||N"

    with open(output_path, 'w', encoding='utf-16') as f:
        cfg.write(f)


def generate_set_file(output_path: Path, inputs: dict, opt_results: dict = None):
    """
    Create a .set file for MT5 testing or optimization.

    Parameters:
    output_path: path to write .set file
    inputs: dict of parameters and optimization metadata
    opt_results: optional dict of fixed values (for OOS testing)
    """
    lines = []

    for key, meta in inputs.items():
        val = meta['default']
        optimize = meta.get('optimize', False)
        if opt_results and key in opt_results:
            val = opt_results[key]
            optimize = False  # force fixed value for OOS

        if optimize:
            min_v = meta.get('min', val)
            max_v = meta.get('max', val)
            step = meta.get('step', 1)
            line = f'{key}={val}||{min_v}||{step}||{max_v}||Y'
        else:
            line = f'{key}={val}||0||0||1||N'

        lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
