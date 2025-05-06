import configparser
import shutil
from pathlib import Path
import logging

from meta_strategist.parsers.report_export import write_xml_to_csv
from meta_strategist.utils.pathing import load_paths

logger = logging.getLogger(__name__)


def copy_mt5_report(ini_path: Path, dest_dir: Path):
    """
    Copies the MT5-generated report (XML) to the results directory
    and generates a CSV version of it.

    param ini_path: Path to the .ini file used for the MT5 run
    param dest_dir: Destination directory for reports
    """
    config = configparser.ConfigParser()
    config.optionxform = str  # Preserve key casing
    config.read(ini_path, encoding="utf-16")

    paths = load_paths()
    report_name = config["Tester"]["Report"]
    src_xml = paths["MT5_ROOT"] / f"{report_name}.xml"
    dest_xml = dest_dir / f"{report_name}.xml"
    dest_csv = dest_dir / f"{report_name}.csv"

    if not src_xml.exists():
        logger.error(f"Report not found: {src_xml}")
        raise FileNotFoundError(f"Report not found: {src_xml}")

    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(src_xml, dest_xml)
    logger.info(f"Copied MT5 XML report to: {dest_xml}")

    try:
        write_xml_to_csv(dest_xml, dest_csv)
        logger.info(f"Converted XML report to CSV: {dest_csv}")
    except Exception as e:
        logger.warning(f"Failed to convert report to CSV: {e}")


def create_dir_structure(run_name: str, indicator_type: str) -> Path:
    """ Create a standardized directory structure for a given run and return the base path.

    param run_name: Name of the run (e.g., zuse, test1)
    param indicator_type: Indicator type folder (e.g., C1, Volume)
    return: Path to the run's base output directory
    """
    paths = load_paths()
    base_path = paths["PRO_ROOT"]
    indi_path = base_path / "Outputs" / run_name / indicator_type

    (indi_path / "experts").mkdir(parents=True, exist_ok=True)
    (indi_path / "ini_files").mkdir(parents=True, exist_ok=True)
    (indi_path / "results").mkdir(parents=True, exist_ok=True)

    logger.info(f"Created directory structure under: {indi_path}")
    return indi_path
