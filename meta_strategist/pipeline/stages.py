

class Stage:
    def __init__(self, name, template_name, post_process_is, depends_on):
        """ Represents a single optimization stage (e.g., 'Trigger', 'Volume').

        param name: Stage name, used in paths and console output
        param template_name: Name of the Jinja2 template file to use for this stage's EA
        param post_process_is: Function to handle parsing IS results and preparing for OOS run
        param depends_on: Optional function to inject constants from previous stages
        """
        self.name = name
        self.template_name = template_name
        self.post_process_is = post_process_is
        self.depends_on = depends_on

    def __repr__(self):
        return f"<Stage {self.name}>"


def get_stage(name: str) -> Stage:
    """ Retrieve a Stage object by its name.
    param name: Name of the stage (e.g., 'Trigger', 'Conformation')
    return: Stage object matching the name
    raises: ValueError if no matching stage is found
    """
    matches = [stage for stage in STAGES if stage.name == name]

    if matches:
        return matches[0]
    else:
        raise ValueError(f"Invalid stage name: '{name}'")


STAGES = [
    Stage(name="Trigger",
          template_name="template_trigger.j2",
          post_process_is="post_process_trigger",
          depends_on=None),

    Stage(name="Conformation",
          template_name="template_conformation.j2",
          post_process_is="post_process_conf",
          depends_on="inject_trigger_results"),

    Stage(name="Volume",
          template_name="template_volume_mq5.j2",
          post_process_is="post_process_volume",
          depends_on="inject_trig_conf_results"),

    Stage(name="Exit",
          template_name="template_exit_mq5.j2",
          post_process_is="post_process_exit",
          depends_on="inject_trig_conf_results"),

    Stage(name="Trendline",
          template_name="template_baseline_mq5.j2",
          post_process_is="post_process_trendline",
          depends_on="inject_all_results"),
]
