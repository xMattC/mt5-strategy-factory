from pathlib import Path
import logging
from meta_strategist.optimise import get_stage
from meta_strategist.gen_ea.stages.trigger import TriggerEAGenerator

logger = logging.getLogger(__name__)


def generate_and_compile_ea(yaml_filename, indi_dir):
    """  Generate and compile a trigger EA based on a YAML config.
    """
    base_dir = Path(__file__).parent / indi_dir
    yaml_path = base_dir / yaml_filename
    compiled_dir = base_dir / "compiled"
    compiled_dir.mkdir(exist_ok=True)

    # Obtain the pipeline stage object for pre-processing/testing
    stage = get_stage("Pre_proc_testing")

    # Instantiate the EA generator with target directory and stage
    generator = TriggerEAGenerator(ea_dir=compiled_dir, stage=stage)

    # Generate one EA based on the provided YAML configuration
    generator.generate_one(yaml_path)

    logger.info(f"Done. Check the '{compiled_dir}' directory for output.")


def process_yaml_file_list(indi_dir, yaml_files):
    """
    Process a given list of YAML filenames within the given directory.
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
            logger.warning(f"{yaml_path} does not exist and will be skipped.")
    return processed


def process_all_yaml_files_in_dir(indi_dir):
    """
    Iterate through all YAML files in the specified directory and process each one.
    """
    base_dir = Path(__file__).parent / indi_dir
    yaml_files = sorted(
        {p.name for ext in ("*.yaml", "*.yml") for p in base_dir.glob(ext)}
    )
    return process_yaml_file_list(indi_dir, yaml_files)


if __name__ == "__main__":
    file_list = [
        "Coral.yaml",
        # "MyOtherIndicator.yaml",
        # ...
    ]
    generated_eas = process_yaml_file_list("trigger", file_list)
    logger.info(f"\nProcessed files: {generated_eas}")

    # For processing all YAML files:
    # generated_eas = process_all_yaml_files_in_dir("trigger")
    # logger.info(f"\nAll processed files: {generated_eas}")
