from pathlib import Path


class StageConfig:
    def __init__(self, name, indi_dir, pipline_dir, ea_generator, ea_template, render_func):
        """Container for a single pipeline stage.

        param name: Stage name (str)
        param renderer: Callable or string import path to the renderer function
        param template: Template file path (str)
        param subfunc: Optional sub-function/callback (callable or string)
        param extra_params: Optional dict of extra settings for this stage
        """
        self.name = name
        self.indi_dir = indi_dir
        self.pipline_dir = pipline_dir
        self.ea_generator = ea_generator
        self.ea_template = ea_template
        self.render_func = render_func

    def __repr__(self):
        return f"<StageConfig {self.name}>"


def get_stage(stages, name: str) -> StageConfig:
    matches = [stage for stage in stages if stage.name == name]
    if matches:
        return matches[0]
    else:
        raise ValueError(f"Invalid stage name: '{name}'")
