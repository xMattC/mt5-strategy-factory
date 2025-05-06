from dataclasses import dataclass
from typing import Dict
import pandas as pd
from pathlib import Path
from xml.sax import parse, ContentHandler
import pandas as pd
from pathlib import Path
from typing import Dict
from dataclasses import dataclass


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







