# pipelines/trend_following.py

"""
Trend-Following Pipeline
------------------------
This pipeline is designed for trending markets.

"""

PIPELINE = [
    {
        "stage": "Trigger",
        "template": "templates.trigger.j2",
        "renderer": "renderers.trigger.py",
    },
    {
        "stage": "Conformation",
        "template": "templates.conformation.j2",
        "renderer": "renderers.conformation.py",
    },
    {
        "stage": "Volume",
        "template": "volume.j2",
        "renderer": "renderers.volume.py",
    },
    {
        "stage": "Exit",
        "template": "exit.j2",
        "renderer": "renderers.exit.py",
    },
    {
        "stage": "Trendline",
        "template": "trendline.j2",
        "renderer": "renderers.trendline.py",
    },
]
