# MT5 Strategy Factory — Configuration Guide

## Overview

This document describes the configuration system used by MT5 Strategy Factory.

The framework uses YAML-based configuration files to separate system behaviour from implementation logic.

Using configuration-driven behaviour allows:

- Repeatable workflows
- Easier experimentation
- Reduced hardcoded values
- Simplified project customisation
- Improved maintainability

The framework primarily uses:

| File | Purpose |
|-------|----------|
| `config.yaml` | Main strategy and execution configuration |
| `whitelist.yaml` | Instrument universe for optimisation |

---

# Configuration Files

Project creation generates:

```text
Project_Name/

├── config.yaml
├── whitelist.yaml
└── run.py
```

---

# config.yaml

`config.yaml` controls:

- execution settings
- optimisation periods
- account settings
- risk management
- stage-specific optimisation behaviour

Example:

```yaml
run_name: Apollo

pipeline: trend_following

whitelist_file: whitelist.yaml

start_date: 2016.01.01
end_date: 2020.01.01

period: D1

main_chart_symbol: EURUSD

currency: USD
deposit: 100000
leverage: 100

data_split: month

risk: 2
sl: 1.5
tp: 1

opt_settings:

  Trigger:

    opt_criterion: 6
    custom_criterion: 1
    min_trade: 100
    max_iterations: 100

  Trendline:

    opt_criterion: 5
    custom_criterion: 99
    min_trade: 20
    max_iterations: 100
```

---

# Configuration Fields

## General Settings

| Field | Description |
|---------|-------------|
| `run_name` | Name of generated project/run |
| `pipeline` | Pipeline implementation to execute |
| `whitelist_file` | Instrument whitelist |
| `period` | Chart timeframe |
| `main_chart_symbol` | Primary chart symbol |
| `currency` | Account currency |
| `deposit` | Initial account balance |
| `leverage` | Account leverage |

---

## Date Configuration

| Field | Description |
|---------|-------------|
| `start_date` | Optimisation start date |
| `end_date` | Optimisation end date |
| `data_split` | IS/OOS split method |

Examples:

```yaml
start_date: 2016.01.01
end_date: 2020.01.01

data_split: month
```

Possible split methods:

- week
- month
- year

Purpose:

Used for:

- In-sample optimisation
- Out-of-sample validation

---

## Risk Settings

| Field | Description |
|---------|-------------|
| `risk` | Percentage risk per trade |
| `sl` | Stop loss setting |
| `tp` | Take profit setting |

Example:

```yaml
risk: 2
sl: 1.5
tp: 1
```

---

# Per-Stage Optimisation Settings

Each stage can define independent optimisation behaviour.

Example:

```yaml
opt_settings:

  Trigger:

    opt_criterion: 6
    custom_criterion: 1
    min_trade: 100
    max_iterations: 100

  Confirmation:

    opt_criterion: 5
    custom_criterion: 99
    min_trade: 50
    max_iterations: 100

  Trendline:

    opt_criterion: 5
    custom_criterion: 99
    min_trade: 20
    max_iterations: 100
```

---

# Optimisation Parameters

## opt_criterion

Determines the MT5 optimisation objective.

Examples:

| Value | Meaning |
|---------|----------|
| `0` | Balance Max |
| `1` | Profit Factor |
| `5` | Custom |
| `6` | Custom Max |

---

## custom_criterion

Custom scoring metric used when custom optimisation is enabled.

Examples:

| Value | Metric |
|---------|----------|
| `0` | Win/Loss Ratio |
| `1` | Win Percentage |
| `99` | Custom internal metric |

---

## min_trade

Minimum trade count required for candidate validity.

Example:

```yaml
min_trade: 100
```

Purpose:

Prevents selection of unstable low-trade results.

---

## max_iterations

Maximum parameter combinations evaluated per indicator.

Example:

```yaml
max_iterations: 100
```

Purpose:

Controls optimisation workload.

---

# whitelist.yaml

Defines the instrument universe used during optimisation.

Example:

```yaml
whitelist:

    - EURUSD
    - GBPUSD
    - AUDNZD
    - EURGBP
    - CHFJPY
```

Purpose:

Controls:

- optimisation instruments
- generated MT5 configurations
- testing scope

---

# Configuration Processing Flow

Configuration loading follows:

```text
config.yaml
        ↓
YAML parsing
        ↓
Validation
        ↓
Configuration object creation
        ↓
Stage execution
```

---

# Common Configuration Issues

## Invalid YAML formatting

Incorrect:

```yaml
risk:2
sl:1.5
```

Correct:

```yaml
risk: 2
sl: 1.5
```

---

## Missing whitelist

Incorrect:

```yaml
whitelist_file: missing.yaml
```

Correct:

```yaml
whitelist_file: whitelist.yaml
```

---

## Invalid dates

Incorrect:

```yaml
start_date: 01/01/2020
```

Correct:

```yaml
start_date: 2020.01.01
```

---

# Design Rationale

The configuration system uses YAML because it:

- separates behaviour from code
- supports reproducible workflows
- simplifies experimentation
- reduces hardcoded values
- allows reusable project definitions
