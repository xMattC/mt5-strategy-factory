from pathlib import Path
from xml.sax import parse, ContentHandler
import pandas as pd
from meta_strategist.reporting.xml_parser import ExcelHandler


def pretty_print_xml_table(xml_path: Path, max_rows: int = 10):
    """Parses and prints a formatted table from an MT5 XML report file.

    param xml_path: Path to the .xml file
    param max_rows: Max number of rows to print
    """
    if not xml_path.exists():
        print(f"[ERROR] File does not exist: {xml_path}")
        return

    handler = ExcelHandler()
    parse(str(xml_path), handler)

    if not handler.tables:
        print("[WARNING] No table data found in XML.")
        return

    df = pd.DataFrame(handler.tables[0][1:], columns=handler.tables[0][0])
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    print(f"\n[INFO] Parsed XML: {xml_path.name}")
    print(df.head(max_rows))  # Show first few rows

    print(f"\n[INFO] Total rows: {len(df)}")


def write_xml_to_csv(xml_path: Path, output_csv_path: Path):
    """ Parse XML and write its full table to a CSV file.

    param xml_path: Path to the MT5 XML result file
    param output_csv_path: Path where the CSV should be saved
    """
    handler = ExcelHandler()
    parse(str(xml_path), handler)

    if not handler.tables:
        print(f"[WARNING] No data found in XML: {xml_path.name}")
        return

    df = pd.DataFrame(handler.tables[0][1:], columns=handler.tables[0][0])
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    print(f"[INFO] Saved XML data to CSV: {output_csv_path.name}")
