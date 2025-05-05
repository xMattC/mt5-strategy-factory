from src.utils import create_structure
from src.ini_generator import IniConfig, generate_all_ini_configs
from src.ea_generator import generate_all_eas
from src.path_config import load_paths
from src.run_ea import run_all_eas


def main(indicator_type: str, base_config: IniConfig):
    """ Main pipeline to generate and run MT5 Expert Advisors based on indicator templates and configurations.

    param indicator_type: Type/category of indicators being processed (e.g., 'C1')
    param base_config: Base configuration object for .ini file generation
    """
    paths = load_paths()  # Load static path settings

    # Create all output folders for this run and get base path
    output_base = create_structure(base_config.run_name, indicator_type)
    ini_files_dir = output_base / 'ini_files'
    compiled_ea_dir = output_base / 'experts'

    # Generate EA source code (.mq5) from template for each indicator YAML
    generate_all_eas(compiled_ea_dir)

    # Generate .ini configuration files for in-sample optimization
    generate_all_ini_configs(expert_dir=compiled_ea_dir, config=base_config, ini_files_dir=ini_files_dir,
                             in_sample=True)

    # Run all in-sample .ini files through MT5 Strategy Tester
    run_all_eas(ini_files_dir)

    # TODO: Process results (e.g., parse XML reports, collect best parameters)

    # TODO: Generate and run out-of-sample .ini files


if __name__ == "__main__":
    INDICATOR_TYPE = 'C1'

    BASE_CONFIG = IniConfig(
        run_name='Apollo',
        start_date="2023.01.01",
        end_date="2023.12.31",
        period="H1",
        custom_criteria="ProfitFactor",
        symbol_mode="ALL",
        data_split="year",
        risk=0.01,
        sl=50,
        tp=100
    )

    main(INDICATOR_TYPE, BASE_CONFIG)
