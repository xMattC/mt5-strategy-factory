import pandas as pd
from pathlib import Path
from typing import Dict
from dataclasses import dataclass


@dataclass
class OptimizationResult:
    indicator_name: str
    parameters: Dict[str, str]


def extract_optimization_result(results_dir: Path, indicator_name: str) -> OptimizationResult:
    """ Extracts optimized parameters from an exported MT5 CSV file.

    param results_dir: Path to the results directory
    param indicator_name: Name of the indicator (used to locate the CSV)
    return: OptimizationResult with best parameter set
    """
    csv_file = results_dir / f"{indicator_name}_IS.csv"
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    df = pd.read_csv(csv_file)

    ignore_cols = {
        'Pass', 'Result', 'Profit', 'Profit Factor', 'Custom', 'Expected Payoff', 'Recovery Factor', 'Sharpe Ratio',
        'Equity DD %', 'Trades'
    }

    param_cols = [col for col in df.columns if col not in ignore_cols]
    best_params = {col.lower(): df.iloc[0][col] for col in param_cols}

    return OptimizationResult(indicator_name=indicator_name, parameters=best_params)
