# MT5 Strategy Factory — Execution Guide

## Overview

This document describes the complete execution flow of MT5 Strategy Factory, from project creation through to final strategy construction.

The framework progressively builds a complete Expert Advisor (EA) by independently evaluating components within a trend-following pipeline.

The implemented process follows:

```text
Project Creation
        ↓
Configuration Loading
        ↓
Trigger Optimisation
        ↓
User Selection
        ↓
Confirmation Optimisation
        ↓
User Selection
        ↓
Trendline Optimisation
        ↓
User Selection
        ↓
Volume Optimisation
        ↓
User Selection
        ↓
Exit Optimisation
        ↓
Final System Construction
```

---

# Execution Entry Points

The framework uses two primary execution files:

| File | Purpose |
|-------|----------|
| `main.py` | Creates and bootstraps a new project |
| `run.py` | Executes the complete optimisation pipeline |

---

# Project Creation (`main.py`)

The framework begins by running:

```bash
python main.py
```

Running this script:

1. Generates a suggested project codename
2. Creates a new project directory
3. Copies required template files
4. Creates:

```text
<ProjectName>/

├── config.yaml
├── whitelist.yaml
└── run.py
```

Generated files:

| File | Description |
|-------|-------------|
| `config.yaml` | Main strategy configuration |
| `whitelist.yaml` | Instrument universe |
| `run.py` | Pipeline execution script |

---

# Configure Project Settings

Before execution, modify:

```yaml
config.yaml
```

Typical settings include:

```yaml
run_name: Apollo

pipeline: trend_following

start_date: 2016.01.01
end_date: 2020.01.01

period: D1

risk: 2
sl: 1.5
tp: 1
```

---

# Define Instrument Universe

Edit:

```yaml
whitelist.yaml
```

Example:

```yaml
whitelist:

  - EURUSD
  - GBPUSD
  - AUDNZD
  - EURGBP
```

The whitelist determines which instruments are included during optimisation and testing.

---

# Execute Pipeline (`run.py`)

Run:

```bash
python run.py
```

This executes:

```python
StageRunner(...)

create_stage_result_yaml(...)
```

The pipeline runs sequentially:

```text
Trigger
    ↓
Confirmation
    ↓
Trendline
    ↓
Volume
    ↓
Exit
```

---

# Stage Definitions

## Trigger

Primary signal used to identify potential trade opportunities.

Examples:

- MACD crossover
- RSI threshold
- Moving average crossover

Purpose:

Identify potential trade entries.

---

## Confirmation

Secondary validation signal used to reduce false positives.

Examples:

- Stochastic agreement
- Momentum confirmation
- Trend strength filters

Purpose:

Improve signal quality.

---

## Trendline

Determines broader market direction.

Examples:

- ALMA
- Hull MA
- EMA
- Trend filters

Purpose:

Align trades with larger trends.

---

## Volume

Additional filter used to remove weak conditions.

Examples:

- Volume indicators
- Volatility filters
- Momentum strength

Purpose:

Avoid low-quality market conditions.

---

## Exit

Defines trade closure behaviour.

Examples:

- ATR exits
- Trailing stops
- Fixed targets
- Risk-based exits

Purpose:

Manage risk and profits.

---

# Stage Execution Flow

Each stage executes the following sequence:

```text
Load indicator definitions
            ↓
Generate MQ5 source files
            ↓
Compile MQ5 → EX5
            ↓
Generate MT5 .ini files
            ↓
Execute MT5 optimisation
            ↓
Parse XML outputs
            ↓
Calculate metrics
            ↓
Generate CSV summaries
            ↓
Pause for user selection
```

---

# Optimisation Workflow

Each generated Expert Advisor performs:

```text
IS Optimisation
        ↓
IS Backtest
        ↓
OOS Evaluation
        ↓
OOS Backtest
        ↓
Score Results
```

Definitions:

| Term | Description |
|-------|-------------|
| IS | In-sample optimisation period |
| OOS | Out-of-sample validation period |

Purpose:

Reduce overfitting and improve robustness.

---

# Result Generation

Following optimisation, outputs are generated:

```text
Outputs/

└── Apollo/

    └── Trigger/

        ├── experts/
        ├── ini_files/
        ├── logs/

        └── results/

            ├── best_summary.csv
            ├── scored_results.csv
            └── the_trigger.yaml
```

Generated files:

| File | Description |
|-------|-------------|
| `best_summary.csv` | Top candidate summary |
| `scored_results.csv` | Full scoring output |
| `the_trigger.yaml` | Selected indicator handoff |

---

# Manual Stage Selection

Following stage completion:

Review:

```text
results/

    best_summary.csv

    scored_results.csv
```

Choose the preferred indicator.

Create the handoff file:

```bash
python -m strategy_factory.post_processing.make_stage_result_file \
--indicator MACD \
--stage Trigger
```

This creates:

```text
Outputs/

└── Apollo/

    └── Trigger/

        └── results/

            the_trigger.yaml
```

---

# Pipeline Pause Behaviour

Execution pauses until:

```text
the_<stage>.yaml
```

exists.

Examples:

```text
the_trigger.yaml
the_confirmation.yaml
the_trendline.yaml
the_volume.yaml
the_exit.yaml
```

This creates a controlled stage-gated workflow where user judgement determines candidate progression.

---

# Common Recovery Actions

## Incorrect indicator selected

Delete:

```text
the_<stage>.yaml
```

Then rerun:

```bash
python run.py
```

---

## Failed MT5 compilation

Check:

```text
Outputs/

    logs/
```

Review compilation output and generated MQ5 files.

---

## Missing output files

Verify:

- MT5 installed correctly
- CLI paths configured
- whitelist valid
- YAML syntax valid

---

# Execution Philosophy

The framework intentionally combines:

- automated processing
- configuration-driven behaviour
- optimisation workflows
- human review

The goal is not complete automation, but progressive construction of higher-quality systems through staged evaluation.
