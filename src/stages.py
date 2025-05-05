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
)

STAGES = [
    {
        "name": "C1",
        "template": "template_c1_mq5.j2",
        "post_process": post_process_c1,
        "depends_on": None,
    },
    {
        "name": "C2",
        "template": "template_c2_mq5.j2",
        "post_process": post_process_c2,
        "depends_on": inject_c1_constants,
    },
    {
        "name": "Volume",
        "template": "template_volume_mq5.j2",
        "post_process": post_process_volume,
        "depends_on": inject_c1_c2_constants,
    },
    {
        "name": "Exit",
        "template": "template_exit_mq5.j2",
        "post_process": post_process_exit,
        "depends_on": inject_c1_c2_constants,
    },
    {
        "name": "Baseline",
        "template": "template_baseline_mq5.j2",
        "post_process": post_process_baseline,
        "depends_on": None,  # or inject_vol_exit_constants
    },
]