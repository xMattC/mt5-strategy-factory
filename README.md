# MT5 Strategy Factory

Python automation framework for systematic MT5 strategy research.

MT5 Strategy Factory generates Expert Advisors (EAs), renders MT5 configuration files, compiles source code through MetaEditor, runs batch optimisations via the MT5 Strategy Tester CLI, and post-processes the results into structured outputs for staged review.

This project is best thought of as an **experiment pipeline for trading strategy development**, not just an EA codebase.

---

## What this project does

MT5 Strategy Factory automates the repetitive parts of quantitative strategy research in MetaTrader 5:

* scaffolds a new strategy research project
* renders EA source code from templates and configuration
* renders MT5 `.ini` files for optimisation and backtesting
* compiles EAs through MetaEditor
* runs large batches of optimisation jobs through the MT5 Strategy Tester CLI
* processes optimisation outputs into structured results
* supports multi-stage strategy construction where each stage builds on the previous one

The current implemented workflow is a **trend-following strategy pipeline**, but the framework is designed so that other pipeline types can be added later.

---

## Why this exists

Manual MT5 strategy development is slow and error-prone when testing many combinations of:

* indicator logic
* parameter ranges
* entry/exit rules
* filters
* in-sample / out-of-sample windows

This framework turns that work into a repeatable pipeline:

1. generate candidate strategy artefacts
2. execute tests in batch
3. collect outputs
4. evaluate results stage by stage
5. carry the best configurations forward

---

## Core idea

A strategy is built as a **pipeline of stages**.

Each stage evaluates a specific class of trading logic:

* trigger
* confirmation
* trendline
* volume
* exit

Each stage:

1. generates EA/config artefacts
2. runs optimisation
3. produces structured results
4. passes best candidates forward

---

## Implemented pipeline: trend-following

### Stage 1 — Trigger

Entry signal generation

### Stage 2 — Confirmation

Signal validation

### Stage 3 — Trendline

Directional bias

### Stage 4 — Volume

Market activity filtering

### Stage 5 — Exit

Exit logic evaluation

---

## Pipeline workflow

```
Strategy template + config
        ↓
Project scaffolding
        ↓
EA / init file rendering
        ↓
MetaEditor compilation
        ↓
MT5 Strategy Tester runs
        ↓
Result collection
        ↓
Post-processing
        ↓
Stage progression
```

---

## What gets automated

* Project scaffolding
* Code generation (MQL5)
* Config generation (.ini files)
* Batch execution
* Result processing
* Multi-stage strategy assembly

---

## Repository structure

```
mt5-strategy-factory/
├── config/
├── docs/
├── indicators/
├── strategy_factory/
│   ├── gen_expert_advisor/
│   ├── gen_initilisation_file/
│   ├── gen_new_project/
│   ├── pipelines/
│   ├── post_processing/
│   ├── renderer_tools/
│   ├── stage_execution/
│   └── utils/
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

---

## Entry point

```
python main.py
```

Creates a new strategy project using the configured pipeline.

---

## Example workflow

1. create project
2. choose pipeline
3. generate EA/config
4. compile EA
5. run MT5 optimisation
6. process results
7. review metrics
8. progress to next stage

---

## Configuration

Configured in:

```
config/local_paths.yaml
```

Example:

```yaml
mt5_root: "..."
mt5_terminal_exe: "..."
mt5_meta_editor_exe: "..."
strategy_factory_root: "..."
```

---

## Requirements

* Python 3.8+
* MetaTrader 5
* MetaEditor
* Access to MT5 Experts directory
* MQL5 include library (`MyLibs`)

---

## Installation

```
git clone https://github.com/xMattC/mt5-strategy-factory.git
cd mt5-strategy-factory

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

---

## Tech stack

* Python
* Jinja2
* pandas / numpy
* PyYAML
* MQL5
* MetaEditor
* MT5 Strategy Tester

---

## Engineering focus

* workflow automation
* batch execution
* template-driven code generation
* staged data processing
* experiment orchestration
* structured result evaluation

---

## Limitations

* requires local MT5 installation
* Windows-dependent
* manual decisions still required between stages
* limited test coverage

---

## Summary

MT5 Strategy Factory is a pipeline-driven framework that transforms manual MT5 strategy development into:

* automated generation
* repeatable execution
* staged optimisation
* structured evaluation

A system designed for scalable and systematic strategy research.
