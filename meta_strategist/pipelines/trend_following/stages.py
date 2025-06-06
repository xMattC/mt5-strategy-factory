from pathlib import Path
from meta_strategist.stage_execution.stage_config import StageConfig

pipline_dir = "meta_strategist.pipelines.trend_following"

STAGES = [

    StageConfig(name="Trigger",
                pipline_dir=pipline_dir,
                indi_dir="trigger",
                render_func=f"{pipline_dir}.renderers.trigger.render_trigger",
                ea_template=Path(Path(__file__).resolve().parent) / "templates" / "trigger.j2"),

    StageConfig(name="Conformation",
                pipline_dir=pipline_dir,
                indi_dir="trigger",
                render_func=f"{pipline_dir}.renderers.conformation.render_conformation",
                ea_template=Path(Path(__file__).resolve().parent) / "templates" / "conformation.j2"),

    # StageConfig(name="Volume", indi_dir="volume"),
    # StageConfig(name="Exit", indi_dir="trigger"),  # indi derived form trigger
    # StageConfig(name="Trendline", indi_dir="trendline"),
]
