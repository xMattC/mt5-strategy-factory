from pathlib import Path
from meta_strategist.pipeline import Stage, get_stage
from meta_strategist.gen_ea.stages.trigger import TriggerEAGenerator
from meta_strategist.utils import init_stage_logger


def _process_yaml_files(indi_dir, yaml_files):
    """ Process a given list of YAML filenames within the given directory.

    param indi_dir: Name or path of the directory containing YAML files
    param yaml_files: List of YAML filenames to process (relative to indi_dir)
    return: List of successfully processed YAML filenames
    """
    base_dir = Path(__file__).parent / indi_dir
    processed = []

    for yaml_name in yaml_files:
        yaml_path = base_dir / yaml_name
        if yaml_path.exists():
            print(f"Processing: {yaml_path.name}")
            main(yaml_name, indi_dir)
            processed.append(yaml_path.name)
        else:
            print(f"Warning: {yaml_path} does not exist and will be skipped.")
    return processed


def process_all_yaml_files_in_dir(indi_dir):
    """ Iterate through all YAML files in the specified directory and process each one.

    param indi_dir: Name or path of the directory containing YAML files
    return: List of successfully processed YAML filenames
    """
    base_dir = Path(__file__).parent / indi_dir
    yaml_files = sorted(
        {p.name for ext in ("*.yaml", "*.yml") for p in base_dir.glob(ext)}
    )
    return _process_yaml_files(indi_dir, yaml_files)


def process_yaml_file_list(indi_dir, yaml_files):
    """ Process a specific list of YAML files within the given directory.

    param indi_dir: Name or path of the directory containing YAML files
    param yaml_files: List of YAML filenames to process (relative to indi_dir)
    return: List of successfully processed YAML filenames
    """
    return _process_yaml_files(indi_dir, yaml_files)


def main(yaml_filename, indi_dir):
    """ Generate and compile a trigger EA based on a YAML config.

    param yaml_filename: Name of the YAML configuration file
    param indi_dir: Name of the indicator directory containing the config
    return: None
    """
    base_dir = Path(__file__).parent / indi_dir
    yaml_path = base_dir / yaml_filename
    compiled_dir = base_dir / "compiled"

    # Create compiled directory if it does not already exist
    compiled_dir.mkdir(exist_ok=True)

    # Obtain the pipeline stage object for pre-processing/testing
    stage = get_stage("Pre_proc_testing")

    # Initialise logger for this stage, logging to the compiled directory
    logger = init_stage_logger(stage.name, compiled_dir)

    # Instantiate the EA generator with target directory and stage
    generator = TriggerEAGenerator(ea_dir=compiled_dir, stage=stage)

    # Generate one EA based on the provided YAML configuration
    generator.generate_one(yaml_path)

    # Log completion message with output location
    logger.info(f"Done. Check the '{compiled_dir}' directory for output.")


if __name__ == "__main__":
    # file_list = [
    #     "Bears_Bulls_Impuls.yaml",
    #     # "MyOtherIndicator.yaml",
    #     # "MyOtherIndicator.yaml",
    #     # "MyOtherIndicator.yaml",
    # ]
    # processed = process_yaml_file_list("trigger", file_list)
    # print(f"\nProcessed files: {processed}")

    all_processed = process_all_yaml_files_in_dir("trigger")
    print(f"\nAll processed files: {all_processed}")
