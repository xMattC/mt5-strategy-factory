from pathlib import Path
import pandas as pd
from xml.etree import ElementTree as ET

import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd


def parse_mt5_results(results_dir: Path):
    """
    Parses all .xml result reports from a directory and combines them into a DataFrame.

    Parameters:
    results_dir: Path to directory containing MT5 .xml result files

    Output:
    Prints a summary and saves a CSV file with all combined results.
    """
    all_results = []

    for xml_file in results_dir.glob("*.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            result = {"file": xml_file.name}

            for field in root.findall("./report/strategytest/*"):
                if field.tag and field.text:
                    result[field.tag] = field.text

            all_results.append(result)
        except ET.ParseError:
            print(f"Warning: Failed to parse {xml_file.name}")

    if not all_results:
        print("No results parsed.")
        return

    df = pd.DataFrame(all_results)
    df.to_csv(results_dir / "combined_results.csv", index=False)
    print("Combined results saved to combined_results.csv")
    print(df.head())


def extract_best_parameters(df: pd.DataFrame, criterion_col: str = "Custom") -> dict:
    """
    Extract the best-performing parameter set from the result DataFrame.

    Parameters:
    df: The DataFrame returned from parse_mt5_xml_results
    criterion_col: Column to rank by (e.g. 'Custom', 'Profit', etc.)

    Returns:
    A dict of parameter names to values (all lowercased).
    """
    if df.empty:
        raise ValueError("Empty result DataFrame")
    if criterion_col not in df.columns:
        raise ValueError(f"'{criterion_col}' column not found in results")

    best = df.sort_values(by=criterion_col, ascending=False).iloc[0]
    param_cols = [col for col in df.columns if col.startswith("Inp")]  # MT5 param names
    return {col.lower(): best[col] for col in param_cols if col in best}
