import logging
from .pathing import load_paths

logger = logging.getLogger(__name__)


def delete_mt5_test_cache():
    """ Deletes all files in the MetaTrader 5 Tester\\cache directory.

    param test_cache_dir: Path to the Tester\\cache directory
    """
    paths = load_paths()
    test_cache_dir = paths["MT5_TEST_CACHE"]
    if test_cache_dir.exists() and test_cache_dir.is_dir():
        deleted = 0
        for file in test_cache_dir.iterdir():
            if file.is_file():
                file.unlink()
                deleted += 1
        logger.info(f"Cleared {deleted} file(s) from MT5 test cache at: {test_cache_dir}")
    else:
        logger.warning(f"MT5 test cache directory does not exist: {test_cache_dir}")
