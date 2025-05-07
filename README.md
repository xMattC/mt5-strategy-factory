# MetaTrader 5 Strategy Optimization Pipeline

This project is a Python-powered framework for automating the strategy development cycle in MetaTrader 5 (MT5). It handles EA generation, compilation, configuration, batch testing, optimisation, and result evaluation — all in a structured, repeatable, and extensible way.

Although created for trading automation, this project demonstrates broader software development skills including:

- Clean Python architecture

- External tool orchestration via CLI

- Template-based code generation (Jinja2)

- XML parsing

- File-based data pipelines

- Modular stage-based processing

- Logging and output structure

## Key Features


- Modular Optimisation Pipeline: Structured per-stage execution (Trigger, Confirmation, Volume, Exit, Baseline, etc.)

- Dynamic EA Templating: Uses Jinja2 to generate .mq5 files from user-defined YAML indicator configurations

- MT5 CLI Integration: Automates EA compilation and strategy testing via metaeditor64.exe and terminal64.exe

- Structured Config Generation: .ini files built per EA and test mode (IS/OOS) with precise parameter control

- Robust XML Parsing: Custom SAX handler to extract results from MT5 XML output files

- Post-Processing: Result aggregation into sorted .csv, summary export, failed test logging

---

## Configuration

Before running the pipeline, you must configure two key areas of the project:

### 1. MetaTrader 5 Paths

Update the hardcoded paths in `meta_strategist/path_config.py` to match your own MetaTrader 5 installation:

```python
# path_config.py
mt5_root = Path(r"C:\Users\YourUser\AppData\Roaming\MetaQuotes\Terminal\YOUR_TERMINAL_ID")
mt5_terminal_exe = Path(r"C:\Program Files\YourBroker MetaTrader 5\terminal64.exe")
mt5_meta_editor_exe = Path(r"C:\Program Files\YourBroker MetaTrader 5\metaeditor64.exe")
```

These paths are used to:
- Locate and compile `.mq5` files
- Run the MT5 Strategy Tester via command-line
- Access test cache, reports, and compiled EAs

### 2. EA Template Structure

By default, EA source files are generated using Jinja2 templates located in:

```
meta_strategist/generators/ea_templates/
```

These templates define how input variables, enums, buffers, and base conditions are inserted into `.mq5` files. Most users will need to adapt these templates to fit their own EA coding conventions, base classes, and project structure.



## Usage

### 1. Create Indicator YAML Files

Place them in `indicators/`. Each file defines inputs, buffer mappings, and optional enums and base conditions:

### 2. Run a Pipeline

```python
from meta_strategist.optimisation_pipeline import OptimizationPipeline
from meta_strategist.ini_generator import IniConfig
from meta_strategist.stages import get_stage

config = IniConfig(
    run_name="Apollo",
    start_date="2023.01.01",
    end_date="2023.12.31",
    period="D1",
    custom_criteria="ProfitFactor",
    symbol_mode="ALL",
    data_split="year",
    risk=0.02,
    sl=2,
    tp=1,
)

stage = get_stage("Trigger")
pipeline = OptimizationPipeline(config=config, stage=stage, recompile_ea=True)
pipeline.run_optimisation()
```

### This will:

1. Generate and compile EAs from YAML + Jinja2

2. Produce .ini files for in-sample runs

3. Run MT5 backtests for each compiled EA

4. Extract optimal parameters

5. Generate .ini for out-of-sample testing using the best in-sample parameters

6. Run out-of-sample tests and parse those results

### 3. Example Output

```
Outputs/{run_name}/{stage_name}/
├── experts/        ← Compiled EAs
├── ini_files/      ← In-sample and OOS .ini configs
├── results/        ← XML reports, combined CSVs
└── logs/           ← Per-stage log output
```
