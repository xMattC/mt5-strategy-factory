import logging
from .pathing import load_paths

logger = logging.getLogger(__name__)


def delete_mt5_test_cache():
    """Deletes all files in the MetaTrader 5 Tester\\cache directory and all .xml files in the MT5 root directory."""
    paths = load_paths()
    test_cache_dir = paths["MT5_TEST_CACHE"]
    mt5_root = paths["MT5_ROOT"]

    # Delete all files in the test cache directory
    deleted_cache = 0
    if test_cache_dir.exists() and test_cache_dir.is_dir():
        for file in test_cache_dir.iterdir():
            if file.is_file():
                file.unlink()
                deleted_cache += 1
        logger.info(f"Cleared {deleted_cache} file(s) from MT5 test cache at: {test_cache_dir}")
    else:
        logger.warning(f"MT5 test cache directory does not exist: {test_cache_dir}")

    # Delete all .xml files in the MT5 root directory
    deleted_xml = 0
    if mt5_root.exists() and mt5_root.is_dir():
        for file in mt5_root.iterdir():
            if file.is_file() and file.suffix.lower() == ".xml":
                file.unlink()
                deleted_xml += 1
        logger.info(f"Cleared {deleted_xml} .xml file(s) from MT5 root at: {mt5_root}")
    else:
        logger.warning(f"MT5 root directory does not exist: {mt5_root}")
