from pathlib import Path

from strategy_factory.pipelines.trend_following.stages import STAGES
from strategy_factory.post_processing.make_stage_result_file import create_stage_result_yaml
from strategy_factory.stage_execution import StageRunner, get_stage_config
from strategy_factory.utils import initialise_logging, load_config_from_yaml, check_and_validate_config

ROOT_DIR = Path(__file__).parent.resolve()


def main():
    """ Entry point for executing the full MT5 optimisation pipeline.

    This script loads and validates the configuration file for the current run, then sequentially executes all
    predefined optimisation stages.

    After each optimisation stage, the user must inspect the results and choose which indicator to pass on to the next
    stage by replacing the placeholder "indicator_tbd" in the result YAML file using `create_stage_result_yaml`.

    This process generates a file named `the_<stage_name>` within the stage's results directory. Overwriting this file
    is disabled. If the user changes their mind about the chosen indicator, they must manually delete the file and rerun
    create_stage_result_yaml.

    Assumes `config.yaml` and `whitelist.yaml` are located alongside this script.
    """

    initialise_logging("compact_full")

    # # --- LOAD PIPELINE CONFIGURATION FILE ---
    config_path = ROOT_DIR / "config.yaml"
    config = load_config_from_yaml(config_path)
    check_and_validate_config(config)
    #
    # # --- TRIGGER STAGE EXECUTION ---
    # stage = get_stage_config(STAGES, "Trigger")
    # StageRunner(project_config=config, stage_config=stage, recompile_ea=True)
    # create_stage_result_yaml("adx", "Trigger", STAGES, ROOT_DIR)
    #
    # # --- CONFORMATION STAGE EXECUTION ---
    # stage = get_stage_config(STAGES, "Conformation")
    # StageRunner(project_config=config, stage_config=stage, recompile_ea=True)
    # create_stage_result_yaml("macd", "Conformation", STAGES, ROOT_DIR)
    #
    # # --- TRENDLINE STAGE EXECUTION ---
    # stage = get_stage_config(STAGES, "Trendline")
    # StageRunner(project_config=config, stage_config=stage, recompile_ea=True)
    # create_stage_result_yaml("sma", "Trendline", STAGES, ROOT_DIR)

    # # --- VOLUME STAGE EXECUTION ---
    # stage = get_stage_config(STAGES, "Volume")
    # StageRunner(project_config=config, stage_config=stage, recompile_ea=True)
    # create_stage_result_yaml("mfi", "Volume", STAGES, ROOT_DIR)

    # # --- EXIT STAGE EXECUTION ---
    stage = get_stage_config(STAGES, "Exit")
    StageRunner(project_config=config, stage_config=stage, recompile_ea=True)


if __name__ == "__main__":
    main()
