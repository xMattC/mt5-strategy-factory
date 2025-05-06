from src.ea_generator import generate_all_eas
from src.ini_generator import IniConfig, generate_all_ini_configs
from src.path_config import load_paths
from src.stages import Stage, get_stage
from src.utils import (
    copy_mt5_report,
    create_dir_structure,
    delete_mt5_test_cache,
    init_stage_logger,
)


class OptimizationPipeline:
    def __init__(self, config: IniConfig, stage: Stage):
        self.config = config
        self.stage = stage
        self.paths = load_paths()
        self.output_base = create_dir_structure(config.run_name, stage.name)
        self.ini_dir = self.output_base / "ini_files"
        self.expert_dir = self.output_base / "experts"
        self.results_dir = self.output_base / "results"
        self.ea_template_path = self.paths["TEMPLATE_DIR"] / self.stage.template_name
        self.logger = init_stage_logger(stage.name, self.output_base)
        delete_mt5_test_cache()

    def run_optimisation(self):
        self.generate_opt_files()

        for ini_file in self.ini_dir.glob("*.ini"):  # Iterate over all .ini files and run each EA individually
            # run_ea(ini_file)
            copy_mt5_report(ini_file, self.results_dir)

    def generate_opt_files(self):
        self.logger.info(f"Generating EAs & IS .ini files for: {self.stage.name} optimisation")
        generate_all_eas(self.expert_dir, self.ea_template_path)
        generate_all_ini_configs(self.expert_dir, self.config, self.ini_dir, True)  # create the in-sample ini files


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
    STAGE = get_stage("C1")
    pipeline = OptimizationPipeline(CONFIG, STAGE)
    pipeline.run_optimisation()
