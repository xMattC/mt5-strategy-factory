"""
Main entry point for generating a new trading system generation project.

Each project is scaffolded using a predefined pipeline template (e.g., 'trend_following') and is assigned a unique
mythological codename, automatically generated in alphabetical order for consistent indexing and reuse prevention.
The output includes boilerplate code, configuration files, and a run script to begin system development and testing.

Key concepts:
    - Modular pipeline stages:
        Each project is structured into logical stages specific to each pipeline. These stages reflect the components
        of a systematic trading strategy and are tested independently.

    - Component iteration:
        For each stage, the framework iterates through a collection of candidate indicators and logic modules. This
        enables broad exploration of potential configurations at each point in the pipeline.

    - Automated testing:
        Every component is automatically optimised and back-tested on both in-sample (IS) and out-of-sample (OOS) data
        splits. This helps evaluate consistency and robustness, and avoids overfitting to training data.

    - System scoring:
        The framework records detailed performance metrics for each component, such as return, draw-down, win rate,
        expectancy, and more. This allows for objective comparison and ranking across options.

    - Manual integration:
        At present, users are responsible for reviewing the results from each stage and selecting which specific
        indicators or logic modules to integrate into the final combined system. Full end-to-end automation of system
        assembly is planned for future releases.

Usage:
    python main.py

Available Pipelines:
    - trend_following : Builds a trend-following strategy with components.

Future support:
    - mean_reversion, breakout, scalping, order-book flow etc.
"""

from strategy_factory.gen_new_project import create_new_project

if __name__ == "__main__":
    create_new_project("trend_following")
