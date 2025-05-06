from xml.sax import parse, ContentHandler


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
