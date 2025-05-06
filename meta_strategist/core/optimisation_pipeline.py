from meta_strategist.parsers.csv_parser import extract_optimization_result, OptimizationResult
from meta_strategist.generators.ea_generator import generate_all_eas, get_compiled_indicators
from meta_strategist.core.ea_runner import run_ea
from meta_strategist.generators.ini_generator import IniConfig, create_ini
from meta_strategist.utils.pathing import load_paths
from meta_strategist.core.stages import Stage, get_stage
from meta_strategist.utils.file_ops import copy_mt5_report, create_dir_structure
from meta_strategist.utils.systems import delete_mt5_test_cache
from meta_strategist.utils.logging import init_stage_logger

# from meta_strategist.post_processing import ResultPostProcessor  # optional


class OptimizationPipeline:
    """ Coordinates the full MT5 optimization process for a single pipeline stage.

    This includes:
    - Setting up output directories and EA templates
    - Running in-sample (IS) and out-of-sample (OOS) optimizations
    - Extracting and logging optimized parameters from test results
    """

    def __init__(self, config: IniConfig, stage: Stage, recompile_ea: bool = True):
        """Initialize the pipeline with config, stage, and EA compilation preference.

        param config: Optimization settings and test parameters
        param stage: Current stage (C1, C2, Volume, Exit, etc.)
        param recompile_ea: Whether to regenerate .mq5 files from templates
        """
        self.config = config
        self.stage = stage
        self.recompile_ea = recompile_ea
        self.paths = load_paths()

        # Set up dirs
        self.output_base = create_dir_structure(self.config.run_name, self.stage.name)
        self.ini_dir = self.output_base / "ini_files"
        self.expert_dir = self.output_base / "experts"
        self.results_dir = self.output_base / "results"
        self.ea_template_path = self.paths["TEMPLATE_DIR"] / self.stage.template_name

        # Initialise logger
        self.logger = init_stage_logger(self.stage.name, self.output_base)

        # Ensure MT5 environment is clean before starting
        delete_mt5_test_cache()

        # Generate or skip EA compilation
        self.generate_expert_advisors()

    def run_optimisation(self):
        """Run IS optimization for all compiled indicators, then OOS tests.
        """
        for indicator in get_compiled_indicators(self.expert_dir):
            self.run_single_optimization(indicator)

    def run_single_optimization(self, indi_name: str):
        """Run IS and (if successful) OOS optimization for a single EA.
        """
        in_sample_result = self.run_optimization(indi_name, in_sample=True)

        if in_sample_result:
            self.run_optimization(indi_name, in_sample=False, result=in_sample_result)

    def run_optimization(self, indi_name: str, in_sample: bool, result: OptimizationResult = None):
        """Run a single optimization pass (IS or OOS) for a given indicator.

        param indi_name: Name of the indicator being optimized
        param in_sample: Whether this is the in-sample phase
        param result: OptimizationResult from IS phase (only required for OOS)
        return: OptimizationResult if IS phase succeeds, otherwise None
        """
        # Generate .ini file for this EA run
        ini_path = create_ini(indi_name=indi_name, expert_dir=self.expert_dir, config=self.config,
                              ini_files_dir=self.ini_dir, in_sample=in_sample,
                              optimized_parameters=result.parameters if result else None)

        if not ini_path:
            self.logger.warning(f"Skipping {indi_name}: missing YAML or EX5.")
            return None

        # Run the test in MT5
        run_ea(ini_path)

        # Copy resulting .csv/.xml reports to results folder
        copy_mt5_report(ini_path, self.results_dir)

        # For IS: extract optimized parameters for use in OOS
        if in_sample:
            return self.extract_result(indi_name)
        else:
            self.logger.info(f"Completed OOS test for {indi_name}")

    def extract_result(self, indi_name: str):
        """ Extract optimized parameters from the result file and log them.

        param indi_name: EA name to extract results for
        return: OptimizationResult if successful, otherwise None
        """
        try:
            result = extract_optimization_result(self.results_dir, indi_name)
            self.logger.info(f"Optimized parameters for {indi_name}: {result.parameters}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to parse optimization result for {indi_name}: {e}")
            return None

    def generate_expert_advisors(self):
        """Compile EA .mq5 files from the template if recompile_ea is True.
        """
        if self.recompile_ea:
            self.logger.info(f"Generating EAs for stage: {self.stage.name}")
            generate_all_eas(self.expert_dir, self.ea_template_path)

        else:
            self.logger.info(f"Skipping EA generation for stage: {self.stage.name}")


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
