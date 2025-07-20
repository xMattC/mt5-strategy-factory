from pathlib import Path
from strategy_factory.stage_execution.stage_config import StageConfig

pipline_dir = "strategy_factory.pipelines.trend_following"
template_dir = Path(__file__).resolve().parent / "templates"

STAGES = [
    StageConfig(
        name="Trigger",
        pipline_dir=pipline_dir,
        indi_dir="trend_following/trigger_conf_exit",  # Assumes in root/indicators dir.
        render_func=f"{pipline_dir}.renderers.trigger.render_trigger",
        ea_template=template_dir / "trigger.j2"
    ),
    StageConfig(
        name="Conformation",
        pipline_dir=pipline_dir,
        indi_dir="trend_following/trigger_conf_exit",
        render_func=f"{pipline_dir}.renderers.conformation.render_conformation",
        ea_template=template_dir / "conformation.j2"
    ),
    StageConfig(
        name="Trendline",
        pipline_dir=pipline_dir,
        indi_dir="trend_following/trendline",
        render_func=f"{pipline_dir}.renderers.trendline.render_trendline",
        ea_template=template_dir / "trendline.j2"
    ),
    StageConfig(
        name="Volume",
        pipline_dir=pipline_dir,
        indi_dir="trend_following/volume",
        render_func=f"{pipline_dir}.renderers.volume.render_volume",
        ea_template=template_dir / "volume.j2"
    ),
    StageConfig(
        name="Exit",
        pipline_dir=pipline_dir,
        indi_dir="trend_following/trigger_conf_exit",
        render_func=f"{pipline_dir}.renderers.exit.render_exit",
        ea_template=template_dir / "exit.j2"
    ),
]
