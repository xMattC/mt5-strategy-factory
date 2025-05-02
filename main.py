from subprocess import run, CalledProcessError
from time import perf_counter
from pathlib import Path

from src.utils import create_structure
from src.ini_generator import IniConfig, generate_all_ini_configs
from src.ea_generator import generate_all_eas
from src.path_config import load_paths


def run_ea(mt5_terminal: Path, ini_file: Path):
    start = perf_counter()
    try:
        run([str(mt5_terminal), f'/config:{ini_file}'], check=True)
        print(f"[INFO] MT5 ran successfully in {perf_counter() - start:.2f}s.")
    except CalledProcessError as e:
        print(f"[ERROR] MT5 failed after {perf_counter() - start:.2f}s. Code: {e.returncode}")
        raise


def main(run_name: str, indicator_type: str, base_config: IniConfig):
    paths = load_paths()
    output_base = paths["PRO_ROOT"] / 'Outputs' / run_name / indicator_type
    ini_output_dir = output_base / 'ini_files'
    compiled_ea_dir = output_base / 'experts'

    # 1. Create output folders
    create_structure(paths["PRO_ROOT"], run_name, indicator_type)

    # 2. Generate Expert Advisors
    template_path = paths["TEMPLATE_DIR"] / 'template_c1_mq5.j2'
    generate_all_eas(template_path, paths["INDICATOR_DIR"], compiled_ea_dir)

    # 3. Update config with actual output dir
    base_config.output_dir = ini_output_dir

    # 4. Generate .ini configs
    generate_all_ini_configs(paths["INDICATOR_DIR"], compiled_ea_dir, base_config, in_sample=False)

    # 5. RUN in sample
    #  run_ea(paths["MT5_TERM_EXE"], ini_file)

    # 6. process data

    # 7. RUN out of sample


if __name__ == "__main__":
    RUN_NAME = 'Apollo'
    INDICATOR_TYPE = 'C1'
    BASE_CONFIG = IniConfig(
        output_dir=Path("tbd"),  # Will be set inside main()
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
    main(RUN_NAME, INDICATOR_TYPE, BASE_CONFIG)
