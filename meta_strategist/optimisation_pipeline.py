from meta_strategist.ea_generator import *
from meta_strategist.ea_runner import run_ea
from meta_strategist.ini_generator import IniConfig, generate_ini_for_indicator
from meta_strategist.path_config import load_paths
from meta_strategist.post_processing import ResultPostProcessor
from meta_strategist.stages import Stage, get_stage
from meta_strategist.utils import (
    copy_mt5_report,
    create_dir_structure,
    delete_mt5_test_cache,
    init_stage_logger,
)
from pathlib import Path
from meta_strategist.utils import ExcelHandler
from xml.sax import parse
import pandas as pd

class OptimizationPipeline:
    """ Controls the full optimization process for a single stage in the MT5 pipeline."""

    def __init__(self, config: IniConfig, stage: Stage, recompile_ea: bool = True):
        """ Initialize pipeline paths, logging, and clean MT5 test cache.
        param config: Configuration object with shared optimization settings
        param stage: Stage object representing current optimization step
        """
        self.config = config
        self.stage = stage
        self.recompile_ea = recompile_ea
        self.paths = load_paths()

        # Create base directory structure for this stage (experts, ini_files, results)
        self.output_base = create_dir_structure(config.run_name, stage.name)
        self.ini_dir = self.output_base / "ini_files"
        self.expert_dir = self.output_base / "experts"
        self.results_dir = self.output_base / "results"

        # Determine which Jinja2 EA template to use for this stage
        self.ea_template_path = self.paths["TEMPLATE_DIR"] / self.stage.template_name

        # Set up logging to stage-specific file in output_base/logs/
        self.logger = init_stage_logger(stage.name, self.output_base)

        # Clean up stale MT5 cache before running
        delete_mt5_test_cache()
        self.generate_expert_advisors()

    def run_optimisation(self):
        """ Perform the in-sample optimization process:"""

        # Iterate through each generated .ini file and handle results
        for indicator_name in get_compiled_indicators(self.expert_dir):
            # ini_path = generate_ini_for_indicator(
            #     indicator_name=indicator_name,
            #     expert_dir=self.expert_dir,
            #     config=self.config,
            #     ini_files_dir=self.ini_dir,
            #     in_sample=True
            # )
            #
            # run_ea(ini_path)
            # copy_mt5_report(ini_path, self.results_dir)
            opt_result = self.get_opt_results_from_xml(indicator_name)
            print(opt_result)

    def generate_expert_advisors(self):
        """Generate:
            - Expert Advisor .mq5 files from YAML indicator templates"""

        if self.recompile_ea:
            self.logger.info(f"Generating EAs files for stage: {self.stage.name}")
            generate_all_eas(self.expert_dir, self.ea_template_path)

        else:
            self.logger.info(f"Skipping EA generation for stage: {self.stage.name}")

    def save_in_sample_opt_results_to_file(self, indicator, lines, lines2):

        file_path = Path.joinpath(self.results_dir, f"{indicator}_opt_results.txt")

        if file_path.is_file():
            file_path.unlink()  # delete old files.

        lines_mod = ''
        for str in lines2:
            lines_mod = lines_mod + str

        print(lines_mod[:-2])

        f = open(file_path, "a")
        f.writelines(indicator + "\n")
        f.writelines(lines)
        f.writelines("\n, ")
        f.write(lines_mod[:-2])
        f.close()

    def get_opt_results_from_xml(self, indicator):

        ins_results = f"{indicator}_IS.xml"
        df = self.load_data_from_xml(self.results_dir, ins_results)
        df = df.drop(['Pass', 'Result', 'Profit', 'Profit Factor', 'Custom', 'Expected Payoff', 'Recovery Factor',
                      'Sharpe Ratio', 'Equity DD %', 'Trades'], axis=1)
        column_names = list(df.columns.values)

        opt_result = []
        for count, value in enumerate(column_names):
            param_results = df[column_names[count]][0]
            tup = (value.lower(), param_results)  # Convert string to lower case.
            opt_result.append(tup)

        return opt_result

    @staticmethod
    def load_data_from_xml(results_dir, file):
        file_path = Path.joinpath(results_dir, file)
        excel_handler = ExcelHandler()
        parse(str(file_path), excel_handler)
        df = pd.DataFrame(excel_handler.tables[0][1:], columns=excel_handler.tables[0][0])
        return df


if __name__ == "__main__":
    CONFIG = IniConfig(
        run_name='Apollo',
        start_date="2023.01.01",
        end_date="2023.12.31",
        period="D1",
        custom_criteria="ProfitFactor",
        symbol_mode="ALL",
        data_split="year",
        risk=0.02,
        sl=2,
        tp=1
    )
    STAGE = get_stage("Trigger")
    pipeline = OptimizationPipeline(config=CONFIG, stage=STAGE, recompile_ea=False)
    pipeline.run_optimisation()
