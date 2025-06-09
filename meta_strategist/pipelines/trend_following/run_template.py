from pathlib import Path

from meta_strategist.stage_execution import StageRunner, get_stage_config
from meta_strategist.utils import (initialise_logging,
                                   load_config_from_yaml,
                                   check_and_validate_config,
                                   create_stage_results_yaml)

# Pipeline-specific import: each pipeline (e.g., trend_following, mean-reversion e.t.c) has a unique STAGES list
from meta_strategist.pipelines.trend_following.stages import STAGES


def make_stage_result_file(phase, indicator):
    """Creates a result file for a given phase and indicator.

    param phase: The optimisation pipeline phase/stage name (e.g., "Trigger", "Volume")
    param indicator: The indicator name or ID to associate with this phase
    """
    # Resolve the current script directory as the base path for result generation
    run_dir = Path(__file__).parent.resolve()

    # Use the 'create_stage_results_yaml' utility to create the stage result file for the given indicator and phase
    create_stage_results_yaml(STAGES, run_dir=run_dir, phase=phase, indicator=indicator)


def main():
    """Entry point for executing a full MT5 optimisation pipeline.

    Loads and validates the configuration file for the current run, then sequentially executes all predefined
    optimisation stages.

    Assumes the config.yaml and whitelist.yaml files are located alongside this script.
    """
    # Set up logging with the 'compact_full' profile.
    initialise_logging("compact_full")

    # Load pipeline configuration from YAML file in the same directory as this script
    config_path = Path(__file__).parent / "config.yaml"
    config = load_config_from_yaml(config_path)

    # Validate the loaded configuration; raises on errors or missing fields
    check_and_validate_config(config)

    # --- TRIGGER STAGE EXECUTION ---
    stage_1 = get_stage_config(STAGES, "Trigger")
    StageRunner(project_config=config, stage_config=stage_1)
    # make_stage_result_file("Trigger", "tbd")

    # --- CONFORMATION STAGE EXECUTION ---
    # stage_2 = get_stage(STAGES, "Conformation")
    # StageRunner(project_config=config, stage_config=stage_2, recompile_ea=True)
    # make_stage_result_file("Conformation", "tbd")

    # --- TRENDLINE STAGE EXECUTION ---
    # stage_5 = get_stage("Trendline")
    # Optimiser(config=config, stage=stage_5).run_stage_optimisations()
    # make_stage_result_file("Trendline", "tbd")

    # --- VOLUME STAGE EXECUTION ---
    # stage_3 = get_stage("Volume")
    # Optimiser(config=config, stage=stage_3).run_stage_optimisations()
    # make_stage_result_file("Volume", "tbd")

    # --- EXIT STAGE EXECUTION ---
    # stage_4 = get_stage("Exit")
    # Optimiser(config=config, stage=stage_4).run_stage_optimisations()
    # make_stage_result_file("Exit", "tbd")


if __name__ == "__main__":
    main()
