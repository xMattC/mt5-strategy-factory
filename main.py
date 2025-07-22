"""
Main entry point for creating a new trading system project.

This sets up a fresh project based on a predefined pipeline template (e.g. 'trend_following') and gives it a unique
mythology-themed codename. The codename is auto-generated in alphabetical order to keep things organised and avoid reuse.

The generated project includes starter code, config files, and a script you can run to start testing and developing.

Key ideas:
    - Pipeline stages:
        Each project is broken into logical stages like confirmation, volume filter, entry trigger, exit, etc. These stages
        match how most trading systems are built and are tested separately.

    - Indicator iteration:
        For each stage, the framework loops through a set of candidate indicators or logic modules to find the best fit.

    - Automated backtesting:
        Every candidate is optimised and back-tested on both in-sample (IS) and out-of-sample (OOS) data. This helps check
        for robustness and avoid overfitting.

    - Scoring:
        The framework logs detailed metrics like return, drawdown, win rate, expectancy, and more — so you can compare options
        objectively.

    - Manual selection:
        For now, you manually review results after each stage and pick which indicators or modules to keep. Full automation
        for system assembly is planned in future versions.

Usage:
    python main.py

Available pipelines:
    - trend_following : Classic trend-following system.

TODO:
    - mean_reversion, breakout, scalping, order-flow, and more.
"""

from strategy_factory.gen_new_project import create_new_project

if __name__ == "__main__":
    create_new_project("trend_following")
