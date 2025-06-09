from pathlib import Path
from typing import Callable, Union
from jinja2 import Environment, FileSystemLoader, Template


class StageConfig:
    """Container for the configuration of a single pipeline stage.

    This class holds all key information required for a pipeline stage, such as its name, where its indicators live,
    which EA template to use, and which function is used to render the EA for this stage.

    param name: Name of the stage (e.g., "Trigger", "Exit")
    param indi_dir: Subdirectory name for indicators used in this stage
    param pipline_dir: Directory path to the parent pipeline (as a Path)
    param ea_template: Path to the Jinja2 template for this stage's EA or a Jinja2 Template object
    param render_func: Callable (render function) or import path string for the render function
    """

    def __init__(self, name: str, indi_dir: str, pipline_dir: str, ea_template: Union[Path, str, Template],
                 render_func: Union[Callable[..., str], str]):

        self.name = name  # Stage name, e.g., "Trigger"
        self.indi_dir = indi_dir  # Indicator subdirectory for this stage
        self.pipline_dir = pipline_dir  # Path to the parent pipeline directory
        self.ea_template = ea_template  # Template path
        self.render_func = render_func  # Callable or import path string

        if isinstance(ea_template, Template):
            pass

        else:
            ea_template_path = Path(ea_template)
            env = Environment(loader=FileSystemLoader(str(ea_template_path.parent)))
            self.ea_template = env.get_template(ea_template_path.name)

    def __repr__(self) -> str:
        return f"<StageConfig {self.name}>"


def get_stage_config(stages, name: str) -> StageConfig:
    """Retrieve a StageConfig object from a list by its name.

    param stages: List of StageConfig objects (e.g., STAGES)
    param name: Name of the stage to look up (case-sensitive)
    return: The matching StageConfig object
    raises ValueError: If no stage with the given name is found
    """
    # Filter all StageConfigs to those with matching name
    matches = [stage for stage in stages if stage.name == name]
    if matches:
        # Return the first match (names should be unique)
        return matches[0]
    else:
        # Raise a clear error if no match is found
        raise ValueError(f"Invalid stage name: '{name}'")
