import sys
import logging
from pathlib import Path


def initialise_pycharm_clickable_logging(level=logging.INFO):
    """Configure logging so PyCharm console makes log lines clickable.
    Should be called as early as possible (before other imports that use logging).
    """
    logging.basicConfig(level=level, format='File "%(pathname)s", line %(lineno)d, in %(funcName)s: %(message)s')


def initialise_logging(fmt_key="simple", date_key="default", log_file: Path = None, level: int = logging.INFO):
    """ Initialise the logging configuration.

    param log_file: Optional path for log file output
    param level: Logging level
    param fmt_key: One of: ("simple", "name", "traceback", "process_thread", "module_func", "pipe")
    param date_key: One of: ("default", "uk", "time_only", "12hr", "short")
    """
    log_format = get_log_format(fmt_key)
    date_format = get_date_fmt(date_key)
    formatter = logging.Formatter(log_format, datefmt=date_format)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove old handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_date_fmt(date_key: str) -> str:
    """Return a date format string based on a key."""
    date_fmts = {
        "default": "%Y-%m-%d %H:%M:%S",
        "uk": "%d/%m/%Y %H:%M:%S",
        "time_only": "%H:%M:%S",
        "12hr": "%I:%M:%S %p",
        "short": "%m-%d %H:%M",
    }
    return date_fmts.get(date_key, date_fmts["default"])


def get_log_format(fmt_key: str) -> str:
    """Return a log format string based on a key."""

    formats = {
        # simple: timestamp, level, message
        # Example: 2025-06-07 22:15:00 [INFO] Started main loop
        "simple": "%(asctime)s [%(levelname)s] %(message)s",

        # name: Adds logger name—useful in multi-module projects
        # Example: 2025-06-07 22:15:00 [INFO] [my_module] Started main loop
        "name": "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",

        # compact_full: Adds logger name—useful in multi-module projects
        # Example: 2025-06-07 15:56:21 [INFO] file.py:function:146 - Started main loop
        "compact_full": "%(asctime)s [%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d - %(message)s",

        # traceback: Python-style traceback, guaranteed clickable in PyCharm
        # Example: File "/path/to/my_script.py", line 42, in do_stuff: Started main loop
        "traceback": 'File "%(pathname)s", line %(lineno)d, in %(funcName)s: %(message)s',

        # process_thread: Great for multiprocessing or multithreaded apps
        # Example: 2025-06-07 22:15:00 1001 139992 INFO Started main loop
        "process_thread": "%(asctime)s %(process)d %(thread)d %(levelname)s %(message)s",

        # Includes module, line, and function—nice for debugging
        # Example: 2025-06-07 22:15:00 INFO my_script:42 do_stuff: Started main loop
        "module_func": "%(asctime)s %(levelname)s %(module)s:%(lineno)d %(funcName)s: %(message)s",

        # pipe: Pipe-separated for easy grep/parsing
        # Example: 2025-06-07 22:15:00 | INFO | my_module | Started main loop
        "pipe": '%(asctime)s | %(levelname)s | %(name)s | %(message)s',

        # short_click: Short clickable PyCharm link (best if unique filenames, must be at line start)
        # Example: my_script.py:42: INFO: Started main loop
        "short_click": "%(filename)s:%(lineno)d: %(levelname)s: %(message)s",

        # json: Structured log, ready for ingestion into ELK, Splunk, etc
        # Example: {"time": "2025-06-07 22:15:00", "level": "INFO", "logger": "my_module", "file": "my_script.py", "line": 42, "msg": "Started main loop"}
        "json": '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "file": "%(filename)s", "line": %(lineno)d, "msg": "%(message)s"}',

        # minimal: Just level and message—great for very terse console logs
        # Example: INFO:Started main loop
        "minimal": "%(levelname)s:%(message)s",

        # all: Everything: useful for debugging weird concurrency or code path issues
        # Example: 2025-06-07 22:15:00 INFO my_module my_script my_script.py:42 do_stuff [PID:1001 TID:139992] Started main loop
        "all": "%(asctime)s %(levelname)s %(name)s %(module)s %(filename)s:%(lineno)d %(funcName)s [PID:%(process)d TID:%(thread)d] %(message)s",

    }

    return formats.get(fmt_key, formats["simple"])
