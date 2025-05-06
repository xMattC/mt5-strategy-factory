import logging
import os
import pandas as pd
from pathlib import Path
from xml.sax import ContentHandler, parse

logger = logging.getLogger(__name__)


class ResultPostProcessor:
    def __init__(self, results_dir: Path, print_summary: bool = True):
        self.results_dir = results_dir
        self.output_file = "1_combined_results.csv"
        self.print_summary = print_summary

    def run(self):
        combined = self._collect_results()
        combined = combined.sort_values("R_outs", ascending=False).reset_index(drop=True)
        output_path = self.results_dir / self.output_file
        combined.to_csv(output_path, index=False)
        logger.info(f"Saved combined results to: {output_path}")

        if self.print_summary:
            print(combined)

    def _collect_results(self) -> pd.DataFrame:
        combined = []
        failed = []

        for file in os.listdir(self.results_dir):
            if not file.endswith("_IS.xml"):
                continue

            prefix = file[:-7]  # remove _ins.xml
            try:
                df_in = self._load_xml_as_df(f"{prefix}_ins.xml")
                df_out = self._load_xml_as_df(f"{prefix}_out.xml")

                result_in = float(df_in["Result"][0])
                result_out = float(df_out["Result"][0])
                pf_in = float(df_in["Profit Factor"][0])
                pf_out = float(df_out["Profit Factor"][0])
                trades_in = float(df_in["Trades"][0])
                trades_out = float(df_out["Trades"][0])

                combined.append({
                    "Indicator": prefix,
                    "R_ins": result_in,
                    "R_outs": result_out,
                    "R_dif": self._percent_diff(result_in, result_out),
                    "R_mean": (result_in + result_out) / 2,
                    "P_fac_in": pf_in,
                    "P_fac_out": pf_out,
                    "P_fac_dif": self._percent_diff(pf_in, pf_out),
                    "trades_in": trades_in,
                    "trades_out": trades_out,
                    "trades_dif": self._percent_diff(trades_in, trades_out)
                })

            except Exception as e:
                logger.warning(f"Failed to process {prefix}: {e}")
                failed.append(prefix)

        if failed:
            failed_path = self.results_dir / "failed_postprocess.txt"
            with open(failed_path, "w") as f:
                f.write("\n".join(failed))
            logger.warning(f"Some indicators failed post-processing. See: {failed_path}")

        return pd.DataFrame(combined)

    def _load_xml_as_df(self, filename: str) -> pd.DataFrame:
        file_path = self.results_dir / filename
        handler = ExcelHandler()
        parse(str(file_path), handler)
        return pd.DataFrame(handler.tables[0][1:], columns=handler.tables[0][0])

    @staticmethod
    def _percent_diff(a: float, b: float) -> float:
        try:
            return round(abs(a - b) / b * 100, 2)
        except ZeroDivisionError:
            return 0.0


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


