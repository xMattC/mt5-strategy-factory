# test_manager.py
from pathlib import Path
from config.config_generator import ConfigGenerator
from core.result_handler import ResultHandler
from core.terminal_executor import TerminalExecutor
from utils.file_tools import list_ex5_indicators, clear_directory


class TestManager:
    def __init__(self, name, start_date, end_date, period, custom_criterion, symbol_mode, data_split):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.period = period
        self.custom_criterion = custom_criterion
        self.symbol_mode = symbol_mode
        self.data_split = data_split

        self.test_root = Path.home() / ".mt5_project" / "tests" / name
        self.indicator_dir = self.test_root / "indicators"
        self.config_dir_in = self.test_root / "configs" / "in_sample"
        self.config_dir_out = self.test_root / "configs" / "out_sample"
        self.results_dir = self.test_root / "results"

        self.config_generator = ConfigGenerator(self)
        self.executor = TerminalExecutor()
        self.result_handler = ResultHandler(self.results_dir)

        self._prepare_dirs()

    def _prepare_dirs(self):
        for d in [self.config_dir_in, self.config_dir_out, self.results_dir]:
            d.mkdir(parents=True, exist_ok=True)
            clear_directory(d)

    def run_tests(self):
        indicators = list_ex5_indicators(self.indicator_dir)
        print("=" * 60)
        print(f"Running tests for {len(indicators)} indicators...")
        for indi in indicators:
            print(f"\n[+] Indicator: {indi}")
            ini_in = self.config_generator.generate(indi, sample_type="in")
            ini_out = self.config_generator.generate(indi, sample_type="out")

            self.executor.run_mt5_test(ini_in)
            self.result_handler.copy_xml(indi, "in")

            self.executor.run_mt5_test(ini_out)
            self.result_handler.copy_xml(indi, "out")
