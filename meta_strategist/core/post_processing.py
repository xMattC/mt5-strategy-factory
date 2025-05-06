import logging
import os
import pandas as pd
from pathlib import Path
from xml.sax import parse

from meta_strategist.parsers.xml_parser import ExcelHandler

logger = logging.getLogger(__name__)


class CombinedResultUpdater:
    """Aggregates in-sample and out-of-sample results from XML reports."""

    def __init__(self, results_dir: Path, stage_name: str = None, print_summary: bool = False):
        """
        param results_dir: Directory containing IS/OOS XML results
        param stage_name: Optional prefix to filter results by indicator stage (e.g., 'C1')
        param print_summary: Whether to print the final combined DataFrame
        """
        self.results_dir = results_dir
        self.stage_name = stage_name
        self.output_file = "1_combined_results.csv"
        self.print_summary = print_summary

    def update(self):
        """Parse and combine all valid XML results, writing stage and full summaries."""
        combined = self._collect_results()

        if combined.empty:
            logger.warning("No valid results collected. Skipping CSV output.")
            return

        combined = combined.sort_values("R_outs", ascending=False).reset_index(drop=True)

        # Write full combined CSV
        full_path = self.results_dir / self.output_file
        combined.to_csv(full_path, index=False)
        logger.info(f"Updated combined results: {full_path}")

        # Optionally write per-stage CSV
        if self.stage_name:
            stage_df = combined[combined["Indicator"].str.startswith(self.stage_name)]
            if not stage_df.empty:
                stage_path = self.results_dir / f"1_combined_results_{self.stage_name}.csv"
                stage_df.to_csv(stage_path, index=False)
                logger.info(f"Updated stage-specific results: {stage_path}")

        if self.print_summary:
            print(combined)

    def _collect_results(self) -> pd.DataFrame:
        """Aggregate IS and OOS metrics from XMLs, skipping any invalid rows."""
        combined = []
        failed = []

        logger.info(f"[PostProcess] Scanning directory: {self.results_dir}")

        for file in os.listdir(self.results_dir):
            if not file.endswith("_IS.xml"):
                continue

            prefix = file[:-7]  # remove "_IS.xml"
            logger.info(f"[PostProcess] Found IS report: {prefix}")

            try:
                df_in = self._load_xml_as_df(f"{prefix}_IS.xml")
                df_out = self._load_xml_as_df(f"{prefix}_OOS.xml")

                result_in = self._safe_float(df_in["Result"][0])
                result_out = self._safe_float(df_out["Result"][0])
                pf_in = self._safe_float(df_in["Profit Factor"][0])
                pf_out = self._safe_float(df_out["Profit Factor"][0])
                trades_in = self._safe_float(df_in["Trades"][0])
                trades_out = self._safe_float(df_out["Trades"][0])

                if any(pd.isna(v) for v in [result_in, result_out, pf_in, pf_out, trades_in, trades_out]):
                    logger.warning(f"Skipping {prefix}: contains NaN or invalid values.")
                    failed.append(prefix)
                    continue

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
        if not file_path.exists():
            raise FileNotFoundError(f"Expected XML result file not found: {file_path}")

        handler = ExcelHandler()
        parse(str(file_path), handler)
        return pd.DataFrame(handler.tables[0][1:], columns=handler.tables[0][0])

    @staticmethod
    def _safe_float(val: str) -> float:
        try:
            val = val.strip().lower()
            if val in {"", "-nan(ind)", "nan", "inf", "-inf"}:
                return float('nan')
            return float(val)
        except Exception:
            return float('nan')

    @staticmethod
    def _percent_diff(a: float, b: float) -> float:
        try:
            return round(abs(a - b) / b * 100, 2)
        except ZeroDivisionError:
            return 0.0
