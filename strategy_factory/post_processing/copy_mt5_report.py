import configparser
import shutil
from pathlib import Path
import logging

from .xml_to_csv import write_xml_to_csv
from strategy_factory.utils import load_paths

logger = logging.getLogger(__name__)


def copy_mt5_report(ini_path: Path, dest_dir: Path):
    """ Copies the MT5-generated report (XML) to the results directory, generates a CSV version of it, and deletes
    the copied XML.

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
        dest_xml.unlink()  # delete the xml version of the results
        logger.info(f"Converted and deleted XML report. CSV saved at: {dest_csv}")
    except Exception as e:
        logger.warning(f"Failed to convert report to CSV: {e}")
