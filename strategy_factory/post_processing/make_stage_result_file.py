from pathlib import Path
import numpy as np
import pandas as pd
import yaml
import logging

from strategy_factory.stage_execution.stage_config import StageConfig, get_stage_config

logger = logging.getLogger(__name__)


def get_output_yaml_path(run_dir: Path, phase: str) -> Path:
    """Get the output YAML file path for a given run and phase.

    param run_dir: Root directory for the run
    param phase: Stage name (e.g., 'Trigger')
    return: Path to the output YAML file
    """
    # Output: run_dir / Trigger / the_trigger.yaml
    phase_cap = phase.capitalize()
    out_dir = run_dir / phase_cap
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"the_{phase.lower()}.yaml"


def find_indicator_yaml(indicators_dir: Path, indicator: str) -> Path:
    """Search for the YAML file matching the indicator name in the given directory.

    param indicators_dir: Directory containing indicator YAML files
    param indicator: Name of the indicator (case-insensitive)
    return: Path to the matching YAML file
    raises: FileNotFoundError if not found
    """
    indicator_lc = indicator.lower()
    for y in indicators_dir.glob("*.yaml"):
        with open(y, "r") as f:
            data = yaml.safe_load(f)
        top_key = next(iter(data)).lower()
        if top_key == indicator_lc:
            return y
    raise FileNotFoundError(f"No YAML found for indicator '{indicator}' in {indicators_dir}")


def extract_minimal_defaults(indicator_yaml: Path) -> tuple[str, dict]:
    """Extract only the default values for all input parameters from the indicator YAML.

    param indicator_yaml: Path to the indicator YAML file
    return: (indicator_name, dict of input defaults)
    """
    with open(indicator_yaml, "r") as f:
        indi_data = yaml.safe_load(f)
    indicator_name = next(iter(indi_data))
    indi_section = indi_data[indicator_name]
    inputs = indi_section.get("indicator_inputs", {})
    minimal = {k: v["default"] for k, v in inputs.items() if "default" in v}

    return indicator_name, minimal


def extract_indicator_optimised_results(run_dir: Path, stage, indicator: str):
    """ Extract the optimised result row for a specific indicator from the combined results CSV.

    Parameters:
    - run_dir : Path to the run directory.
    - stage : StageConfig object with a .name attribute (e.g., 'confirmation').
    - indicator : Name of the indicator (e.g., 'macd').

    Returns:
    - dict of result values for the indicator, or None if not found.
    """
    results_file = run_dir / str(stage.name) / "results" / f"{indicator}_IS.csv"

    if not results_file.exists():
        raise FileNotFoundError(f"Parameter-level results file not found: {results_file}")

    df = pd.read_csv(results_file)

    if df.empty:
        raise ValueError(f"No data in: {results_file}")

    # Sort by Result, take the top row
    best = df.sort_values("Result", ascending=False).iloc[0]

    # List of known output/stat columns to exclude
    non_param_cols = {
        "Pass", "Result", "Profit", "Expected Payoff", "Profit Factor", "Recovery Factor",
        "Sharpe Ratio", "Custom", "Equity DD %", "Trades"
    }

    # Anything not in the above list is assumed to be an input parameter
    param_cols = [col for col in df.columns if col not in non_param_cols]

    optimised_inputs = {col: best[col] for col in param_cols}
    return optimised_inputs


def merge_optimised_params(defaults: dict, optimised: dict) -> dict:
    """ Merge defaults with optimised values, keeping optimised where provided.

    param defaults: dict of default parameter values
    param optimised: dict of optimised values (e.g. from CSV)

    return: Merged dict with optimised values where available
    """
    merged = {}

    for key in defaults:
        if key in optimised:
            val = optimised[key]
            # Convert NumPy numbers to native Python types
            if isinstance(val, (np.integer, np.floating)):
                val = val.item()
            merged[key] = val
        else:
            merged[key] = defaults[key]

    return merged


def create_stage_yaml(run_dir: Path, stage: StageConfig, indicator: str):
    """Create a minimal stage YAML for a specific indicator and stage.

    param run_dir: Root directory for the run
    param stage: Stage object (determines indicator subdirectory)
    param indicator: Name of the indicator to use
    param out_filename: Optional custom output filename
    """
    # Determine the root indicators directory, and use the subdirectory for the stage if needed
    indicators_dir = Path(__file__).resolve().parents[2] / "indicators"
    if getattr(stage, "indi_dir", None):
        indicators_dir = indicators_dir / stage.indi_dir

    # Find the YAML file for the requested indicator
    indicator_yaml = find_indicator_yaml(indicators_dir, indicator)

    # Extract minimal input defaults
    indicator_name, indi_defaults = extract_minimal_defaults(indicator_yaml)

    # Replace default values with optimised results values
    indi_opt_vals = extract_indicator_optimised_results(run_dir, stage, indicator)

    # Create final dir which includes the optimised results.
    indi_final_values = merge_optimised_params(indi_defaults, indi_opt_vals)

    # Determine the output YAML file path (use custom if provided)
    out_path = get_output_yaml_path(run_dir, stage.name)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Prevent overwrite unless the user deletes the old file
    if out_path.exists():
        logger.info(f"YAML file already exists: {out_path}\nPlease delete it if you need to remake.")
        return

    # Write the minimal YAML (only defaults for inputs) to the output file
    with open(out_path, "w") as f:
        yaml.dump({indicator_name: indi_final_values}, f, sort_keys=False, indent=2)
    logger.info(f"Stage YAML created: {out_path}")


def create_stage_result_yaml(indicator: str, phase: str, stages, run_dir: Path):
    """ Convenience entry point to be called from a wrapper script.

    param indicator: Indicator name (e.g., 'aroon', 'aso')
    param phase: Name of the stage (e.g., 'trigger', 'conformation')
    param STAGES: project stage object.
    param run_dir: Root directory for this run (defaults to the script's directory)
    """
    if run_dir is None:
        run_dir = Path(__file__).parent.resolve()  # Use script location if not given

    stage = get_stage_config(stages, phase.capitalize())  # Get the Stage object for this phase

    create_stage_yaml(run_dir, stage, indicator)
