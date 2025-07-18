from pathlib import Path
import logging
from meta_strategist.stage_execution import StageConfig
from meta_strategist.utils import load_paths, initialise_logging, ProjectConfig

from meta_strategist.gen_expert_advisor.generate_ea import GenerateEA

logger = logging.getLogger(__name__)


def generate_and_compile_ea(yaml_filename, indi_dir):
    """Generate and compile a trigger EA based on a YAML config.
    """
    # Prepare directories
    base_dir = Path(__file__).parent / indi_dir
    yaml_path = base_dir / yaml_filename
    compiled_dir = base_dir / "compiled"
    compiled_dir.mkdir(exist_ok=True)

    # Set up project config:
    project_config = ProjectConfig(run_name="TestRun",
                                   pipeline="pre_process_test",
                                   whitelist=["Symbol()"])

    # Build stage config:
    paths = load_paths()
    pipline_dir = "meta_strategist.pipelines.pre_process_test"
    stage_config = StageConfig(name="pre_proc_test",
                               indi_dir=indi_dir,  # This should be just the subdirectory name, not a full path
                               pipline_dir=pipline_dir,
                               render_func=f"{pipline_dir}.render_file.render_pre_proc_test",
                               ea_template=paths["PIPELINE_DIR"] / "pre_process_test" / "ea_template.j2")

    # Generate the EA
    GenerateEA(project_config, stage_config, compiled_dir).generate_one(yaml_path)
    logger.info(f"Done. Check the '{compiled_dir}' directory for output.")


def process_yaml_file_list(indi_dir, yaml_files):
    """Process a given list of YAML filenames within the given directory.
    """
    base_dir = Path(__file__).parent / indi_dir
    processed = []

    for yaml_name in yaml_files:
        yaml_path = base_dir / yaml_name
        if yaml_path.exists():
            logger.info(f"Processing: {yaml_path.name}")
            generate_and_compile_ea(yaml_name, indi_dir)
            processed.append(yaml_path.name)
        else:
            logger.info(f"{yaml_path} does not exist and will be skipped.")
    return processed


def process_all_yaml_files_in_dir(indi_dir):
    """ Iterate through all YAML files in the specified directory and process each one.
    """
    base_dir = Path(__file__).parent / indi_dir
    yaml_files = [p.name for p in base_dir.glob("*.yaml")]
    return process_yaml_file_list(indi_dir, yaml_files)


if __name__ == "__main__":
    # Main execution entry point for EA generation.
    #
    # Description:
    # - Initialises logging in compact_full mode for structured output.
    # - Processes all YAML configuration files from the "mt5_built_in_indicators"
    #   directory to generate corresponding Expert Advisors (EAs).
    # - Alternative processing paths are provided via commented lines to enable
    #   specific subsets of files or different strategy categories (e.g.,
    #   trend-following triggers, volume filters, etc.).
    #
    # Logic:
    # - Logging is configured first for debug visibility.
    # - You can either uncomment a specific `file_list` or directory-based
    #   processing line depending on what subset of EAs you wish to generate.
    # - The final list of generated EAs is printed to the console.
    initialise_logging("compact_full")

    # file_list = [
    #     "mt5_ac.yaml",
    #     # "mt5_Force.yaml",
    #     # "mt5_MFI.yaml",
    #     # "mt5_StdDev.yaml",
    #     # "mt5_Stochastic.yaml",
    #     # "mt5_Volumes.yaml",
    # ]

    generated_eas = process_all_yaml_files_in_dir("mt5_built_in_indicators")
    # generated_eas = process_yaml_file_list("trend_following/trigger_conf_exit", file_list)

    # generated_eas = process_all_yaml_files_in_dir("trend_following/trigger_conf_exit")
    # generated_eas = process_yaml_file_list("trend_following/trigger_conf_exit", file_list)

    # generated_eas = process_all_yaml_files_in_dir("trend_following/trendline")
    # generated_eas = process_yaml_file_list("trend_following/trendline", file_list)

    # generated_eas = process_all_yaml_files_in_dir("trend_following/volume")
    # generated_eas = process_yaml_file_list("trend_following/volume", file_list)

    print(f"\nAll processed files: {generated_eas}")
