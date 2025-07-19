import yaml
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

# Metrics to exclude when extracting parameter columns
METRIC_COLUMNS = {
    "Pass", "Result", "Profit", "Expected Payoff", "Profit Factor", "Recovery Factor",
    "Sharpe Ratio", "Custom", "Equity DD %", "Trades"
}


def extract_top_parameters(
        results_dir: Path,
        top_n: int = 5,
        sort_by: str = "Res_OOS",
        csv_file: str = "1_top_parameter_sets.csv",
        yaml_file: str = "1_top_parameter_sets.yaml"
):
    """
    Extract best IS parameters for the top-N indicators based on the combined results CSV.

    Writes both a flat CSV (for humans) and structured YAML (for automation).

    param results_dir: Directory containing combined results and IS CSVs
    param top_n: Number of top indicators to extract
    param sort_by: Metric to sort on (e.g. 'Res_OOS', 'PF_OOS')
    param csv_file: Output CSV file name
    param yaml_file: Output YAML file name
    """
    combined_path = results_dir / "1_combined_results.csv"
    if not combined_path.exists():
        raise FileNotFoundError(f"Combined results not found: {combined_path}")

    df = pd.read_csv(combined_path)

    if sort_by not in df.columns:
        raise ValueError(f"Sort column '{sort_by}' not found in combined results.")

    top_df = df.sort_values(sort_by, ascending=False).head(top_n)
    top_indicators = top_df["Indicator"].tolist()

    extracted_rows = []
    extracted_yaml = {}

    for name in top_indicators:
        is_csv = results_dir / f"{name}_IS.csv"
        if not is_csv.exists():
            logger.warning(f"Missing IS CSV: {is_csv}")
            continue

        df_is = pd.read_csv(is_csv).sort_values("Result", ascending=False)
        if df_is.empty:
            continue

        param_cols = [col for col in df_is.columns if col not in METRIC_COLUMNS]
        param_values = df_is.iloc[0][param_cols].to_dict()

        # For CSV (flat)
        extracted_rows.append({
            "Indicator": name,
            **param_values
        })

        # For YAML (nested)
        extracted_yaml[name] = param_values

    if not extracted_rows:
        logger.warning("No parameter sets extracted.")
        return

    # Save CSV
    csv_path = results_dir / csv_file
    pd.DataFrame(extracted_rows).to_csv(csv_path, index=False)
    logger.info(f"[INFO] Saved top {top_n} parameter sets to: {csv_path}")

    # Save YAML
    yaml_path = results_dir / yaml_file
    with open(yaml_path, "w") as f:
        yaml.dump(extracted_yaml, f, sort_keys=False)
    logger.info(f"[INFO] Saved YAML parameter sets to: {yaml_path}")
