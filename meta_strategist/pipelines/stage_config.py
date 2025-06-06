class StageConfig:
    def __init__(
            self,
            name,
            renderer,
            template,
            subfunc=None,
            extra_params=None
    ):
        """Container for a single pipeline stage.

        param name: Stage name (str)
        param renderer: Callable or string import path to the renderer function
        param template: Template file path (str)
        param subfunc: Optional sub-function/callback (callable or string)
        param extra_params: Optional dict of extra settings for this stage
        """
        self.name = name
        self.renderer = renderer
        self.template = template
        self.subfunc = subfunc
        self.extra_params = extra_params or {}

    def __repr__(self):
        return f"<StageConfig {self.name}>"
