import logging
import os
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

# Constants
IS_SUFFIX = "_IS.csv"
OOS_SUFFIX = "_OOS.csv"
SUMMARY_FILE = "1_combined_results.csv"
STAGE_SUMMARY_TEMPLATE = "1_combined_results_{stage}.csv"
FAILED_LIST_FILE = "failed_postprocess.txt"

# Metric columns to extract and summarize
METRICS = {
    "Res": "Result",
    "PF": "Profit Factor",
    "Trades": "Trades"
}


def update_combined_results(results_dir: Path, stage_name: str = None, print_summary: bool = False):
    """ Aggregate IS/OOS results from CSVs and write combined summaries.

    param results_dir: Directory containing *_IS.csv and *_OOS.csv result files
    param stage_name: Optional filter to generate stage-specific summary (e.g., 'C1')
    param print_summary: If True, prints the full combined DataFrame to console
    """
    combined, failed = collect_results(results_dir)

    if combined.empty:
        logger.warning("No valid results found.")
        return

    # Sort by best out-of-sample result
    combined = combined.sort_values("Res_OOS", ascending=False).reset_index(drop=True)

    # Save full summary CSV
    combined.to_csv(results_dir / SUMMARY_FILE, index=False)
    logger.info("Saved combined results.")

    # Save stage-specific CSV if applicable
    if stage_name:
        stage_df = combined[combined["Indicator"].str.startswith(stage_name)]
        if not stage_df.empty:
            stage_path = results_dir / STAGE_SUMMARY_TEMPLATE.format(stage=stage_name)
            stage_df.to_csv(stage_path, index=False)
            logger.info(f"Saved stage-specific results: {stage_path.name}")

    # Log any failures
    if failed:
        with open(results_dir / FAILED_LIST_FILE, "w") as f:
            f.write("\n".join(failed))
        logger.warning("Some indicators failed post-processing.")

    if print_summary:
        print(combined)


def collect_results(results_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    """ Parse *_IS.csv and *_OOS.csv pairs and extract summary metrics.

    param results_dir: Path to the results directory
    return: Tuple of (DataFrame with results, List of indicator names that failed)
    """
    rows = []
    failed = []

    for file in os.listdir(results_dir):
        if not file.endswith(IS_SUFFIX):
            continue

        name = file.replace(IS_SUFFIX, "")

        try:
            df_in = load_csv_as_df(results_dir / f"{name}{IS_SUFFIX}")
            df_out = load_csv_as_df(results_dir / f"{name}{OOS_SUFFIX}")

            # Sort explicitly by Result (in case MT5 didn't)
            df_in = df_in.sort_values("Result", ascending=False)
            df_out = df_out.sort_values("Result", ascending=False)

            row = build_combined_row(name, df_in, df_out)
            if row:
                rows.append(row)
            else:
                failed.append(name)

        except Exception as e:
            logger.warning(f"Failed to process {name}: {e}")
            failed.append(name)

    return pd.DataFrame(rows), failed


def load_csv_as_df(csv_path: Path) -> pd.DataFrame:
    """ Load a CSV file into a DataFrame.

    param csv_path: Path to a .csv file
    return: Parsed DataFrame
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing file: {csv_path}")
    return pd.read_csv(csv_path)


def build_combined_row(indicator: str, df_in: pd.DataFrame, df_out: pd.DataFrame) -> dict | None:
    """ Construct a single summary row from top IS/OOS CSV entries.

    param indicator: Name of the indicator
    param df_in: In-sample results as DataFrame (already sorted by Result)
    param df_out: Out-of-sample results as DataFrame (already sorted by Result)
    return: Dictionary of summary metrics or None if invalid
    """
    try:
        values = {}

        for key, col in METRICS.items():
            values[f"{key}_IS"] = safe_float(df_in[col].iloc[0])
            values[f"{key}_OOS"] = safe_float(df_out[col].iloc[0])

        # Skip any result with missing or invalid metrics
        if any(pd.isna(v) for v in values.values()):
            return None

        # Return combined summary row
        return {
            "Indicator": indicator,
            **values,
            "Res_dif": percent_diff(values["Res_IS"], values["Res_OOS"]),
            "Res_mean": (values["Res_IS"] + values["Res_OOS"]) / 2,
            "PF_dif": percent_diff(values["PF_IS"], values["PF_OOS"]),
            "Trades_dif": percent_diff(values["Trades_IS"], values["Trades_OOS"]),
        }

    except Exception as e:
        logger.warning(f"Error building row for {indicator}: {e}")
        return None


def safe_float(val: str) -> float:
    """ Convert a value to float, treating invalid values as 0.0.

    param val: Value from CSV (str, float, or int)
    return: Float-safe representation
    """
    try:
        v = str(val).strip().lower()
        return 0.0 if v in {"", "nan", "inf", "-inf", "-nan(ind)"} else float(v)

    except Exception:
        return 0.0


def percent_diff(a: float, b: float) -> float:
    """  Compute percentage difference between two values.

    param a: First value
    param b: Second value
    return: Percent difference (rounded), or 0.0 if b is zero
    """
    try:
        return round(abs(a - b) / b * 100, 2)

    except ZeroDivisionError:
        return 0.0
