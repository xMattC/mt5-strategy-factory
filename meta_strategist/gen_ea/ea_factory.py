import logging
from pathlib import Path

from .stages.trigger import TriggerEAGenerator
from .stages.conformation import ConformationEAGenerator

logger = logging.getLogger(__name__)


def get_ea_generator(stage, ea_dir: Path, run_name: str):
    """ Factory function for EA generators.

    Returns a generator instance appropriate for the given optimisation stage. All generator
    objects returned from this function implement the public interface of `BaseEAGenerator`,
    including the `.generate_all()` method.

    param stage: The current optimisation pipeline stage.
    param ea_dir: Directory where EA source and binaries will be managed.
    param run_name: The name of the current optimisation run.
    return: An instance of a subclass of `BaseEAGenerator`.
    """
    if stage.name == "Trigger":
        return TriggerEAGenerator(ea_dir, stage)

    elif stage.name == "Conformation":
        assert run_name is not None, "run_name must be provided for Conformation stage"
        return ConformationEAGenerator(ea_dir, stage, run_name)

    # Add other stages...

    else:
        raise ValueError(f"No EA generator defined for stage: {stage.name}")



