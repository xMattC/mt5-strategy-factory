# === Core Pipeline Components ===
from meta_strategist.pipeline.stages import Stage, get_stage
from meta_strategist.pipeline.mt5_ea_runner import run_ea

# === Generators ===
from meta_strategist.generators.ea_generator import generate_all_eas, get_compiled_indicators
from meta_strategist.generators.ini_generator import IniConfig, create_ini

# === Reporting ===
from meta_strategist.reporting.csv_parser import extract_optimization_result, OptimizationResult
from meta_strategist.reporting.result_summary import update_combined_results
from meta_strategist.reporting.extract_top_parameters import extract_top_parameters

# === Utilities ===
from meta_strategist.utils.pathing import load_paths
from meta_strategist.utils.file_ops import copy_mt5_report, create_dir_structure
from meta_strategist.utils.systems import delete_mt5_test_cache
from meta_strategist.utils.logging import init_stage_logger


class Optimization:
    """ Coordinates the full MT5 optimization process for a single pipeline stage.

    Responsibilities:
    - Create directory structures and generate EA + .ini files
    - Run in-sample (IS) and out-of-sample (OOS) tests
    - Extract and log optimised parameters
    - Update and combine performance summaries
    """

    def __init__(self, config: IniConfig, stage: Stage, recompile_ea: bool = True):
        """ Initialise the optimization pipeline.

        param config: Settings and trading parameters for MT5 tests
        param stage: Pipeline stage (e.g. Trigger, Conformation, Volume, etc.)
        param recompile_ea: Whether to generate new EAs from template
        """
        self.config = config
        self.stage = stage
        self.recompile_ea = recompile_ea
        self.paths = load_paths()

        # Set up output folders
        self.output_base = create_dir_structure(self.config.run_name, self.stage.name)
        self.ini_dir = self.output_base / "ini_files"
        self.expert_dir = self.output_base / "experts"
        self.results_dir = self.output_base / "results"

        # Locate EA template file
        self.ea_template_path = self.paths["TEMPLATE_DIR"] / self.stage.template_name

        # Set up logging for this stage
        self.logger = init_stage_logger(self.stage.name, self.output_base)

        # Clean MT5 environment
        delete_mt5_test_cache()

        # Optionally generate EAs from templates (if recompile_ea = True)
        self.generate_expert_advisors()

    def run_optimisation(self):
        """ Run optimisation for all compiled indicators (EAs) in this stage.
        Performs both IS and OOS tests, and combines results.
        """
        for indicator in get_compiled_indicators(self.expert_dir):
            self.run_single_optimization(indicator)

            # Update results table after each EA is processed
            update_combined_results(
                results_dir=self.results_dir,
                stage_name=self.stage.name,
                print_summary=False
            )

        # Extract and save top-N performing parameter sets after all are done
        extract_top_parameters(
            results_dir=self.results_dir,
            top_n=5,
            sort_by="Res_OOS"
        )

    def run_single_optimization(self, indi_name: str):
        """ Run IS and OOS tests for a single EA (indicator).

        param indi_name: The name of the compiled EA/indicator
        """
        in_sample_result = self.run_optimization(indi_name, in_sample=True)

        # Only proceed to OOS if IS result is valid
        if in_sample_result:
            self.run_optimization(indi_name, in_sample=False, result=in_sample_result)

    def run_optimization(self, indi_name: str, in_sample: bool, result: OptimizationResult = None):
        """ Run a single IS or OOS optimization pass.

        param indi_name: EA name
        param in_sample: True for IS phase, False for OOS
        param result: Required only for OOS; the IS result parameters
        return: OptimizationResult for IS phase, else None
        """
        # Generate .ini config file for this run
        ini_path = create_ini(
            indi_name=indi_name,
            expert_dir=self.expert_dir,
            config=self.config,
            ini_files_dir=self.ini_dir,
            in_sample=in_sample,
            optimized_parameters=result.parameters if result else None
        )

        if not ini_path:
            self.logger.warning(f"Skipping {indi_name}: missing YAML or EX5.")
            return None

        # Launch MT5 test run
        run_ea(ini_path)

        # Save .csv/.xml reports to results directory
        copy_mt5_report(ini_path, self.results_dir)

        # For IS: extract result for use in OOS
        if in_sample:
            return self.extract_result(indi_name)

        self.logger.info(f"Completed OOS test for {indi_name}")

    def extract_result(self, indi_name: str):
        """ Parse result file to extract optimized parameters.

        param indi_name: EA name to extract from
        return: OptimizationResult object or None if parsing fails
        """
        try:
            result = extract_optimization_result(self.results_dir, indi_name)
            self.logger.info(f"Optimized parameters for {indi_name}: {result.parameters}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to parse optimization result for {indi_name}: {e}")
            return None

    def generate_expert_advisors(self):
        """ Generate EA .mq5 files from template if recompile_ea is enabled.
        """
        if self.recompile_ea:
            self.logger.info(f"Generating EAs for stage: {self.stage.name}")
            generate_all_eas(self.expert_dir, self.ea_template_path)
        else:
            self.logger.info(f"Skipping EA generation for stage: {self.stage.name}")


# === Example Run ===
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

    pipeline = Optimization(config=CONFIG, stage=STAGE, recompile_ea=False)
    pipeline.run_optimisation()
