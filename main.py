from pathlib import Path
# from mt5_pipeline.ea_generator import generate_eas_from_yaml
from dev_dir.config_generator import generate_ini_config
from mt5_pipeline.runner import run_mt5_test
from mt5_pipeline.results_parser import parse_mt5_results  # coming soon

# --- Configurable paths ---
# yaml_dir = Path("indicators")
eas_dir = Path("ea")  # generated .mq5 files
compiled_ea_dir = Path("C:/Users/mkcor/AppData/Roaming/MetaQuotes/Terminal/49CDDEAA95A409ED22BD2287BB67CB9C/MQL5/Experts/meta-strategist/outputs_dir/ea")
config_dir = compiled_ea_dir

results_dir = Path("C:/Users/mkcor/AppData/Roaming/MetaQuotes/Terminal/49CDDEAA95A409ED22BD2287BB67CB9C/MQL5/Experts/meta-strategist/outputs_dir/results")

# # --- 1. Generate EA files from YAML ---
# generate_eas_from_yaml(yaml_dir, eas_dir)

# --- 2. Create .ini config for each EA ---
for ea_path in compiled_ea_dir.glob("*.ex5"):
    name = ea_path.stem
    ini_path = config_dir / f"{name}.ini"
    inputs = {}  # Load parsed input params from YAML or elsewhere

    generate_ini_config(
        expert_path=(Path("C:/Users/mkcor/AppData/Roaming/MetaQuotes/Terminal/49CDDEAA95A409ED22BD2287BB67CB9C/MQL5/Experts")),
        output_path=ini_path,
        start_date="2012.01.01",
        end_date="2022.01.01",
        period="Daily",
        custom_criteria="4",
        symbol_mode="1",
        data_split="month",
        risk=2.0,
        sl=1.5,
        tp=1.0,
        report_name=f"{name}_ins",
        inputs=inputs
    )

# --- 3. Run MT5 tests ---
mt5_terminal_path = Path(r"C:/Program Files/FTMO MetaTrader 5/terminal64.exe")

for ini_file in config_dir.glob("*.ini"):
    run_mt5_test(mt5_terminal_path, ini_file)

# --- 4. Post-process results (coming soon) ---
parse_mt5_results(results_dir)
