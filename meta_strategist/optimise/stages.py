class Stage:
    def __init__(self, name, indi_dir=None):
        """Represents a single optimisation stage (e.g., 'Trigger', 'Volume').

        param name: Stage name
        param template_name: Jinja2 template file for this stage's EA
        param indi_dir: Subdirectory within INDICATOR_DIR for this stage's indicators
        """
        self.name = name
        self.indi_dir = indi_dir  # e.g., "trigger", "volume", etc. (or None for default)

    def __repr__(self):
        return f"<Stage {self.name}>"


def get_stage(name: str) -> Stage:
    """ Retrieve a Stage object by its name.
    param name: Name of the stage (e.g., 'Trigger', 'Conformation')
    raises: ValueError if no matching stage is found
    """
    matches = [stage for stage in STAGES if stage.name == name]

    if matches:
        return matches[0]
    else:
        raise ValueError(f"Invalid stage name: '{name}'")


STAGES = [
    Stage(name="Pre_proc_testing", indi_dir="indicators"),
    Stage(name="Trigger", indi_dir="trigger"),
    Stage(name="Conformation", indi_dir="trigger"),  # indi derived form trigger
    Stage(name="Volume", indi_dir="volume"),
    Stage(name="Exit", indi_dir="trigger"),  # indi derived form trigger
    Stage(name="Trendline", indi_dir="trendline"),
]
