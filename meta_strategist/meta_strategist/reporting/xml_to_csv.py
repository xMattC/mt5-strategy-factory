from xml.sax import parse, ContentHandler
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def write_xml_to_csv(xml_path: Path, output_csv_path: Path):
    """ Parse XML and write its full table to a CSV file.

    param xml_path: Path to the MT5 XML result file
    param output_csv_path: Path where the CSV should be saved
    """
    handler = ExcelHandler()
    parse(str(xml_path), handler)

    if not handler.tables:
        logger.info(f"[WARNING] No data found in XML: {xml_path.name}")
        return

    df = pd.DataFrame(handler.tables[0][1:], columns=handler.tables[0][0])
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    logging.info(f"[INFO] Saved XML data to CSV: {output_csv_path.name}")


class ExcelHandler(ContentHandler):
    def __init__(self):
        self.tables = []
        self.chars = []

    def characters(self, content):
        self.chars.append(content)

    def startElement(self, name, attrs):
        if name == "Table":
            self.rows = []
        elif name == "Row":
            self.cells = []
        elif name == "Data":
            self.chars = []

    def endElement(self, name):
        if name == "Table":
            self.tables.append(self.rows)
        elif name == "Row":
            self.rows.append(self.cells)
        elif name == "Data":
            self.cells.append("".join(self.chars))
