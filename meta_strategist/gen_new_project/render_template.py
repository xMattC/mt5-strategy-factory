import logging
from meta_strategist.utils.pathing import load_paths
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


def render_template(template_name: str, context: dict) -> str:
    """Renders a Jinja2 template from the templates directory."""
    paths = load_paths()
    env = Environment(
        loader=FileSystemLoader(paths["TEMPLATE_DIR"]),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template(template_name)
    return template.render(context)
