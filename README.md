# MT5 Strategy Factory
 
![Strategy Factory Banner](docs/image.png)

**MetaTrader 5 (MT5)** is a multi-asset trading platform widely used for developing and executing automated trading 
strategies. [Learn more](https://www.metatrader5.com/en)

## Overview

**MT5 Strategy Factory** is a modular framework for building full-featured Expert Advisors (EAs) from configurable trading logic components. It enables systematic 
strategy development by combining automation, indicator modularity, and robust evaluation tools. The framework compiles EAs directly via **MetaEditor** and executes 
large-scale batch optimisations using the **MetaTrader 5 Strategy Tester CLI**, streamlining the entire research and development workflow.

Whether you're a quantitative trader, algorithmic developer, or strategy engineer, this framework enables you to rapidly prototype, test, and refine trading strategies in a structured, repeatable, and scalable way.

The system is built around the concept of **strategy pipelines** — multi-stage processes that assemble, optimise, and validate EAs from modular parts. The currently
implemented pipeline is a **trend-following system**, but the architecture is fully extensible: advanced users can define and implement **custom pipelines** tailored 
to other trading styles, such as mean reversion, breakout, or scalping strategies.

This flexibility makes MT5 Strategy Factory a robust foundation for automated trading research, development, and deployment across a wide range of market hypotheses.

## Trend-Following Pipeline

The currently implemented system follows a **trend-following architecture**, structured as a multi-stage pipeline. At each stage, a specific category of indicators is evaluated and optimised. These stages build upon one another to form a cohesive, high-performance trading system:

### Trigger Stage
This initial stage focuses on identifying the core signal generator of the strategy — the **Trigger**. A pool of candidate indicators is tested and optimised individually, using in-sample (IS) data. The goal is to isolate indicators capable of consistently generating entry signals under the defined market conditions.

### Confirmation Stage
Once a Trigger has been selected, the **Confirmation** stage evaluates indicators that filter or validate the Trigger signals. These indicators are tested in combination with the chosen Trigger to ensure complementary behaviour. Only those that improve robustness and reduce false signals are advanced.

### Trendline Stage
Here, the pipeline evaluates **Trendline**-based filters or conditions, which aim to confirm broader market structure. These are optimised in conjunction with both the Trigger and Confirmation indicators, assessing their contribution to overall strategy alignment with trending conditions.

### Volume Stage
Volume filters are introduced to avoid poor-quality signals during low-liquidity periods or to emphasise signals occurring during significant market participation. This stage uses the cumulative logic from previous phases and tests **Volume** indicators for added precision and robustness.

### Exit Stage
The final stage determines how trades are exited. This includes evaluating and optimising **Exit** logic such as fixed stops, trailing stops, ATR-based exits, or indicator-driven closures. Exit rules are tested in the context of the entire trading stack built up in the previous stages.

### Decision Points and Evaluation

After **each stage**, the user is responsible for reviewing performance metrics and selecting which indicator (or configuration) to carry forward. 
This allows for human oversight and strategic decision-making between stages, ensuring only the most promising components are retained.

Each stage is scored independently using a **user-defined performance metric**, such as:

- Profit Factor  
- Sharpe Ratio  
- Expected Payoff  
- Custom-defined scoring functions

Optimisations are performed on **in-sample (IS)** data to tune parameters, followed by **out-of-sample (OOS)** testing to validate generalisability. 
This two-phase process is critical for detecting and avoiding **curve fitting** — a common pitfall in algorithmic development where strategies appear 
effective in-sample but fail in real-world conditions.

Indicators that fail to show consistent OOS performance are discarded, regardless of their in-sample results. This ensures that the resulting system 
is not only optimised, but also resilient and deployable in live trading conditions.

### Final Outcome

The end result is a fully constructed, tested, and deployable Expert Advisor — built from individually selected, data-validated 
components — with minimal manual intervention and a strong emphasis on generalisation and robustness.

More details on the implemented trend-following system can be found here: [Trendfollowing - System](https://github.com/xMattC/mt5-strategy-factory/blob/main/docs/Trendfollowing%20-%20%20system%20concept.md)

## Use Cases

- Quantitative developers building, testing, and refining modular strategies
- Algo researchers evaluating signal performance across time
- System traders seeking reproducible, automated backtesting workflows

## Requirements

- Python 3.8+
- MetaTrader 5 (installed and licensed locally)
- Access to your MT5 `Experts/` folder


## Aditional Dependency: MyLibs MQL5 Utility Library

This strategy framework depends on a companion MQL5 utility library containing reusable classes for:

- Trade execution and management
- Risk control and position sizing
- Signal state tracking and indicator handling
- Time-based filters and session controls

To use this framework successfully, you **must install the `MyLibs` library** into your MetaTrader 5 terminal.


1. Download or clone the required library:
   ( [mt5-quant-lib](https://github.com/xMattC/mt5-quant-lib) )

2. Place the `MyLibs` folder in your MetaTrader 5 `Include/` directory:

```plaintext
C:/Users/<YourUsername>/AppData/Roaming/MetaQuotes/Terminal/<YourInstanceID>/MQL5/Include/MyLibs/
```


## MT5 Strategy Factory Installation

#### Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/xMattC/mt5-strategy-factory.git
cd mt5-strategy-factory
```

#### Step 2: Set Up a Virtual Environment

Create a virtual environment to manage dependencies e.g:

```bash
python -m venv .env
```

Activate the virtual environment:

- On Windows:
  ```bash
  .env\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source .env/bin/activate
  ```

#### Step 3: Install Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure to clone this repo directly into your MT5 Experts folder:

```
C:/Users/YourUser/AppData/Roaming/MetaQuotes/Terminal/YOUR_TERMINAL_ID/MQL5/Experts
```

## Configuration
Update the paths in ../mt5-strategy-factory/config/local_paths.yaml:
```yaml
mt5_root: "C:/Users/YourUser/AppData/Roaming/MetaQuotes/Terminal/YOUR_TERMINAL_ID"

mt5_terminal_exe: "C:/Program Files/YourBroker MetaTrader 5/terminal64.exe"

mt5_meta_editor_exe: "C:/Program Files/YourBroker MetaTrader 5/metaeditor64.exe"

strategy_factory_root: "C:/Users/YourUser/AppData/Roaming/MetaQuotes/Terminal/YOUR_TERMINAL_ID/MQL5/Experts/mt5-strategy-factory"
```

# MT5 Strategy Factory – Execution Guide

This guide describes the complete strategy execution flow in **MT5 Strategy Factory**, including how to use `main.py`, configure your strategy, and run the full trend-following pipeline using `run.py`.

The MT5 Strategy Factory is designed to run via a single entry point: `main.py`. This script bootstraps your strategy project, scaffolds the required files, and prepares everything needed to begin optimisation.

### What Happens When You Run `main.py`

1. A **project codename** is suggested using a generator.
2. If the user accepts (`Y`), a new project directory is created with:
   - `config.yaml` – strategy configuration
   - `whitelist.yaml` – list of tradable instruments
   - `run.py` – ready-to-execute pipeline script
3. The user can customise the generated config before running `run.py`.

---

### `run.py`: Stage Execution Script

This script orchestrates the execution of each logical strategy stage in order:

```python
StageRunner(...)                # Optimises the stage
create_stage_result_yaml(...)   # Creates placeholder for indicator handoff
```

After each stage, the system halts until a user manually chooses the best-performing indicator to forward to the next stage.

A file like this must be created:

```
Outputs/{run_name}/{stage_name}/results/the_{stage_name}.yaml
```

Until this file exists, execution of the pipeline will pause.

**Note:** If a mistake is made, delete the `the_{stage}.yaml` file manually and rerun the helper script.

---

### config.yaml – Strategy Configuration

This YAML file contains all critical parameters for test configuration, including risk, time periods, and per-stage settings.

### Base Configuration Example

```yaml
run_name: example_run # Generated project name 
pipeline: trend_following # The name of the strategy pipeline to use (e.g., trend_following, mean_reversion)
whitelist_file: whitelist.yaml  # Path to the whitelist file. Use either "whitelist.yaml" or "CART_SYMBOL_ONLY"
start_date: 2016.01.01 # Optimisation/testing data start date (YYYY.MM.DD)
end_date: 2020.01.01 # Optimisation/testing data end date (YYYY.MM.DD)
period: D1 # Chart timeframe/period (e.g., D1 = daily, H1 = hourly)
main_chart_symbol: EURUSD # Main chart symbol for this run (not necessarily traded)
currency: USD # Base currency for trade account
deposit: 100000 # Initial deposit for the account (in currency units)
leverage: 100 # Account leverage (e.g., 100 = 1:100)
data_split: month # How to split the data for in-sample/out-of-sample (e.g., week, month, year)
risk: 2 # Default trade risk per position (as a percent of account, e.g., 2%)
sl: 1.5 # Default stop loss value (in ATR or custom units; pipeline-specific)
tp: 1 # Default take profit value (in ATR or custom units; pipeline-specific)
```

### Per-Stage Optimisation Settings

```yaml
opt_settings:
  Trigger:
    opt_criterion: 6       # 6 = Custom Max
    custom_criterion: 1    # Only used if opt_criterion = 6. (0=WIN_LOSS_RATIO, 1=WIN_PERCENT)
    min_trade: 100         # Minimum trades required for a valid solution
    max_iterations: 100    # Maximum optimisation params per indicator/ indicator param.

  Trendline:
    opt_criterion: 5
    custom_criterion: 99
    min_trade: 20
    max_iterations: 100
```

---

## whitelist.yaml – Symbol Universe

Defines tradable pairs or assets for testing:

```yaml
whitelist:
  - EURUSD
  - AUDNZD
  - EURGBP
  - AUDCAD
  - CHFJPY
```

Used during `.ini` generation to build config files for MT5’s strategy tester.

---

### How the Pipeline Works

Each stage is defined as a `stage_config` and is run in the following order:

1. **Trigger**
2. **Confirmation**
3. **Trendline**
4. **Volume**
5. **Exit**

Each stage:
- Loads indicators from YAML
- Compiles `.mq5` to `.ex5`
- Generates `.ini` strategy tester configs
- Runs MT5 via CLI
- Parses and scores XML result files
- Outputs CSV summaries and YAML metadata

---

### Indicator Selection Between Stages

After a stage completes, the user must:

1. Inspect:
   - `results/best_summary.csv`
   - `results/scored_results.csv`
2. Select a winning indicator
3. Use the helper:

```bash
python -m strategy_factory.post_processing.make_stage_result_file --indicator <name> --stage Trigger
```

This will create:

```
Outputs/{run_name}/{stage_name}/results/the_{stage_name}.yaml
```

This is **required** to continue the pipeline.

---

### Output Folder Layout

```
Outputs/
└── Apollo/
    ├── Trigger/
    │   ├── experts/
    │   ├── ini_files/
    │   ├── results/
    │   └── logs/
    ├── Confirmation/
    ├── Trendline/
    ├── Volume/
    └── Exit/
```



## Roadmap

- Trend-following pipeline complete
- Breakout, mean-reversion and scalping pipelines
- Walk-forward testing framework
- Monte Carlo testing for backtest results
- Integrated visual reporting dashboard

### Contributing
Contributions and ideas of all kinds are welcome! Feel free to fork the project and submit a pull request, or open an issue to start a discussion.

Note: This repository serves as a proof of concept. Active development is maintained in a private repository. If you're interested in collaborating more closely, please don’t hesitate to reach out.
