import logging
from pathlib import Path

from .stages.trigger import TriggerEAGenerator
from .stages.conf import ConformationEAGenerator
# from .stages.volume import VolumeEAGenerator
# from .stages.exit import ExitEAGenerator
# from .stages.trendline import TrendlineEAGenerator

logger = logging.getLogger(__name__)


def get_ea_generator(stage, ea_dir: Path, run_name: str):
    """ Entry point for the "gen_ea" package.
    Return the appropriate EA generator instance for the given pipeline stage.

    For a given optimisation pipeline stage, returns an instance of the correct EA generator class, each of which
    implements the public interface of `BaseEAGenerator` from "base.py" (including `.generate_all()`).

    param stage: The current optimisation pipeline stage (should have a .name attribute).
    param ea_dir: Path to the directory where EA source and binaries will be managed.
    param run_name: The name of the current optimisation run.
    returns: Instance of a subclass of `BaseEAGenerator` for this stage.
    raises: ValueError if no suitable generator exists for the provided stage.
    """

    if stage.name == "Trigger":
        return TriggerEAGenerator(ea_dir, stage, run_name)

    elif stage.name == "Conformation":
        assert run_name is not None, "run_name must be provided for Conformation stage"
        return ConformationEAGenerator(ea_dir, stage, run_name)

    # elif stage.name == "Volume":
    #     # assert run_name is not None, "run_name must be provided for Volume stage"
    #     return VolumeEAGenerator(ea_dir, stage)
    #
    # elif stage.name == "Exit":
    #     # assert run_name is not None, "run_name must be provided for Exit stage"
    #     return ExitEAGenerator(ea_dir, stage)
    #
    # elif stage.name == "Trendline":
    #     # assert run_name is not None, "run_name must be provided for Trendline stage"
    #     return TrendlineEAGenerator(ea_dir, stage)

    else:
        raise ValueError(f"No EA generator defined for stage: {stage.name}")

