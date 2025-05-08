import logging
from pathlib import Path

from meta_strategist.pipeline.stages import get_stage
from meta_strategist.pipeline.optimisation import Optimization
from meta_strategist.utils.filesystems import load_config_from_yaml

logger = logging.getLogger(__name__)


def trend_following_strategy_generator(path_to_config: Path):
    """ Run a multi-stage optimisation pipeline for a trend-following strategy.
    This includes the following stages in order:
    Trigger -> Conformation -> Volume -> Exit -> Trendline

    param path_to_config: Path to a YAML config file defining run settings
    """
    config = load_config_from_yaml(path_to_config)

    stage_sequence = ["Trigger", "Conformation", "Volume", "Exit", "Trendline"]
    for stage_name in stage_sequence:
        logger.info(f"Starting optimisation stage: {stage_name}")
        stage = get_stage(stage_name)
        pipeline = Optimization(config=config, stage=stage)
        pipeline.run_optimisation()
