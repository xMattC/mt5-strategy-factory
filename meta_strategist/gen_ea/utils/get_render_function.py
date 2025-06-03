from meta_strategist.gen_ea.stages.trigger import render_trigger_ea
from meta_strategist.gen_ea.stages.conformation import render_conformation_ea
# from .volume import render_volume_ea
# from .exit import render_exit_ea
# from .baseline import render_baseline_ea


def get_render_function(ea_type: str):
    """Return the appropriate rendering function based on the EA type.

    param ea_type: Name of the EA stage/type (must match dictionary keys)
    return: Callable that accepts (template, indicator_name, data) and returns the rendered source code as str
    raises: KeyError if the EA type is unknown
    """
    # Map EA type string to the appropriate render function
    return {
        "Trigger": render_trigger_ea,
        "Conformation": render_conformation_ea,
        # "Volume": render_volume_ea,
        # "Exit": render_exit_ea,
        # "Trendline": render_baseline_ea,
    }[ea_type]

