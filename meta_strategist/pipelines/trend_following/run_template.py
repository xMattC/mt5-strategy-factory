from pathlib import Path
from meta_strategist.utils import initialise_logging, load_config_from_yaml, check_and_validate_config
from meta_strategist.stage_execution import StageRunner, get_stage
from meta_strategist.utils import maker

from meta_strategist.pipelines.trend_following.stages import STAGES  # unique for each pipeline


def make_stage_result_file(phase, indicator):
    run_dir = Path(__file__).parent.resolve()
    maker(STAGES, run_dir=run_dir, phase=phase, indicator=indicator)


def main():
    """Entry point for executing a full MT5 optimisation pipeline.

    Loads and validates the configuration file for the current run, then sequentially executes all predefined
    optimisation stages (e.g., Trigger, Conformation, Volume, Exit, Trendline) using the same configuration.

    Assumes the config.yaml, and whitelist.yaml files are next to this script.
    """
    initialise_logging("compact_full")

    # Load configuration YAML for this run
    config_path = Path(__file__).parent / "config.yaml"
    config = load_config_from_yaml(config_path)
    check_and_validate_config(config)

    stage_1 = get_stage(STAGES, "Trigger")
    StageRunner(project_config=config, stage_config=stage_1)

    # make_stage_result_file("Trigger", "tbd")

    # stage_2 = get_stage(STAGES, "Conformation")
    # StageRunner(project_config=config, stage_config=stage_2, recompile_ea=True)

    # make_stage_result_file("Conformation", "tbd")

    # stage_3 = get_stage("Volume")
    # Optimiser(config=config, stage=stage_3).run_stage_optimisations()

    # make_stage_result_file("Volume", "tbd")

    # stage_4 = get_stage("Exit")
    # Optimiser(config=config, stage=stage_4).run_stage_optimisations()

    # make_stage_result_file("Exit", "tbd")

    # stage_5 = get_stage("Trendline")
    # Optimiser(config=config, stage=stage_5).run_stage_optimisations()


if __name__ == "__main__":
    main()
