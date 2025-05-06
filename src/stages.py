from src.post_processing import (
    post_process_c1,
    post_process_c2,
    post_process_volume,
    post_process_exit,
    post_process_baseline,
)

from src.dependencies import (
    inject_c1_constants,
    inject_c1_c2_constants,
    inject_all_constants,
)


class Stage:
    def __init__(self, name, template_name, post_process_is, depends_on):
        """ Represents a single optimization stage (e.g., 'C1', 'Volume') in the MT5 pipeline.

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
    return next(stage for stage in STAGES if stage.name == name)


STAGES = [
    Stage(name="C1",
          template_name="template_c1_mq5.j2",
          post_process_is=post_process_c1,
          depends_on=None),

    Stage(name="C2",
          template_name="template_c2_mq5.j2",
          post_process_is=post_process_c2,
          depends_on=inject_c1_constants),

    Stage(name="Volume",
          template_name="template_volume_mq5.j2",
          post_process_is=post_process_volume,
          depends_on=inject_c1_c2_constants),

    Stage(name="Exit",
          template_name="template_exit_mq5.j2",
          post_process_is=post_process_exit,
          depends_on=inject_c1_c2_constants),

    Stage(name="Baseline",
          template_name="template_baseline_mq5.j2",
          post_process_is=post_process_baseline,
          depends_on=inject_all_constants),
]
