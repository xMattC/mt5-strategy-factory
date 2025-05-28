from meta_strategist.gen_ea import get_ea_generator_for_stage
from meta_strategist.gen_config import IniConfig, create_ini
from meta_strategist.reporting import (
    extract_optimization_result,
    OptimizationResult,
    update_combined_results,
    extract_top_parameters,
    copy_mt5_report
)
from meta_strategist.utils import (
    load_paths,
    create_dir_structure,
    get_compiled_indicators,
    delete_mt5_test_cache,
    init_stage_logger
)
from .stages import Stage
from .mt5_ea_runner import run_ea


class Optimiser:
    """ Coordinates the full MT5 optimisation process for a single pipeline stage.

    param config: IniConfig object containing run parameters
    param stage: Stage object defining this optimisation phase
    param recompile_ea: If True, force EA regeneration from template
    """

    def __init__(self, config: IniConfig, stage: Stage, recompile_ea: bool = True):
        """ Initialise the optimiser pipeline.

        param config: IniConfig object containing run parameters
        param stage: Stage object for this pipeline step
        param recompile_ea: If True, force EA regeneration from template
        """
        self.config = config
        self.stage = stage
        self.recompile_ea = recompile_ea
        self.paths = load_paths()

        # Set up output folder structure for this run/stage
        self.output_base = create_dir_structure(self.config.run_name, self.stage.name)
        self.ini_dir = self.output_base / "ini_files"
        self.expert_dir = self.output_base / "experts"
        self.results_dir = self.output_base / "results"

        # Locate the EA template file for this stage
        self.ea_template_path = self.paths["TEMPLATE_DIR"] / self.stage.template_name

        # Set up logging for this stage/run
        self.logger = init_stage_logger(self.stage.name, self.output_base)

        # Clean the MT5 environment (delete cache)
        delete_mt5_test_cache()

        # Optionally (re)generate all EAs for this stage
        self.generate_experts()

    def generate_experts(self):
        """ Generate EA .mq5 files from template if recompile_ea is enabled. """
        if self.recompile_ea:
            self.logger.info(f"Generating EAs for stage: {self.stage.name}")
            generator = get_ea_generator_for_stage(self.stage, self.expert_dir, self.config.run_name)
            generator.generate_all()

        else:
            self.logger.info(f"Skipping EA generation for stage: {self.stage.name}")

    def run_stage_optimisations(self):
        """ Run optimisation for all compiled indicators (EAs) in this stage. """
        for indicator in get_compiled_indicators(self.expert_dir):
            self.optimise_indicator(indicator)

            # ALWAYS update the combined results table
            update_combined_results(results_dir=self.results_dir, stage_name=self.stage.name, print_summary=False)

        # Finally, extract top-N performing parameter sets
        extract_top_parameters(results_dir=self.results_dir, top_n=5, sort_by="Res_OOS")

    def optimise_indicator(self, indi_name: str):
        """ Run IS and OOS tests for a single EA (indicator).

        param indi_name: Base name of the EA/indicator
        """
        # --- In-sample pass ---
        if self._has_is_results(indi_name):

            is_csv = self.results_dir / f"{indi_name}_IS.csv"
            self.logger.info(f"Skipping in-sample optimisation for {indi_name}: found existing {is_csv}")

            try:
                is_result = extract_optimization_result(self.results_dir, indi_name)
                self.logger.info(f"Extracted existing in-sample result for {indi_name}: {is_result.parameters}")

            except Exception as e:
                self.logger.error(f"Failed to parse existing in-sample result for {indi_name}: {e}")
                is_result = None
        else:
            is_result = self.run_in_sample(indi_name)

        # --- Out-of-sample pass ---
        if is_result:

            if self._has_oos_results(indi_name):
                oos_csv = self.results_dir / f"{indi_name}_OOS.csv"
                self.logger.info(f"Skipping out-of-sample optimisation for {indi_name}: found existing {oos_csv}")

            else:
                self.run_out_of_sample(indi_name, is_result)

    def run_in_sample(self, indi_name: str) -> OptimizationResult | None:
        """ Run the in-sample (IS) optimisation pass.

        param indi_name: Base name of the EA/indicator
        return: OptimizationResult object or None if failed
        """
        ini_path = create_ini(indi_name=indi_name, expert_dir=self.expert_dir, config=self.config,
                              ini_files_dir=self.ini_dir, in_sample=True, optimized_parameters=None)

        if not ini_path:
            self.logger.warning(f"Skipping {indi_name}: missing YAML or EX5.")
            return None

        run_ea(ini_path)
        copy_mt5_report(ini_path, self.results_dir)

        try:
            result = extract_optimization_result(self.results_dir, indi_name)
            self.logger.info(f"Optimised parameters for {indi_name} (IS): {result.parameters}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to parse optimisation result for {indi_name} (IS): {e}")
            return None

    def run_out_of_sample(self, indi_name: str, optimisation_result: OptimizationResult):
        """ Run the out-of-sample (OOS) optimisation pass.

        param indi_name: Base name of the EA/indicator
        param optimisation_result: OptimizationResult from IS phase
        """
        ini_path = create_ini(indi_name=indi_name, expert_dir=self.expert_dir, config=self.config,
                              ini_files_dir=self.ini_dir, in_sample=False,
                              optimized_parameters=optimisation_result.parameters)

        if not ini_path:
            self.logger.warning(f"Skipping OOS for {indi_name}: missing YAML or EX5.")
            return

        run_ea(ini_path)
        copy_mt5_report(ini_path, self.results_dir)
        self.logger.info(f"Completed OOS test for {indi_name}")

    def _has_is_results(self, indi_name: str) -> bool:
        """ Check if an in-sample results file already exists.

        param indi_name: Base name of the EA/indicator
        return: True if IS results CSV exists, else False
        """
        return (self.results_dir / f"{indi_name}_IS.csv").exists()

    def _has_oos_results(self, indi_name: str) -> bool:
        """ Check if an out-of-sample results file already exists.

        param indi_name: Base name of the EA/indicator
        return: True if OOS results CSV exists, else False
        """
        return (self.results_dir / f"{indi_name}_OOS.csv").exists()
