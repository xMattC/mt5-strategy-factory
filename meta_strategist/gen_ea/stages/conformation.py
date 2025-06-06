import logging
from pathlib import Path

from jinja2 import Template

from meta_strategist.optimise import Stage, get_stage
from ..base import BaseEAGenerator
from ..ea_utils import load_indicator_data, build_input_lines, build_enum_definitions, load_results_data

logger = logging.getLogger(__name__)


class ConformationEAGenerator(BaseEAGenerator):
    """EA generator for the Conformation stage.

    param ea_output_dir: Output directory for EAs
    param stage: The current Stage object
    param run_name: The optimisation run name (used to find trigger output)
    """

    def __init__(self, ea_output_dir: Path, stage: Stage, run_name: str, whitelist:list):
        """Initialise the ConformationEAGenerator.

        param ea_output_dir: Directory where EAs will be output
        param stage: Current pipeline Stage object
        param run_name: Optimisation run name
        """
        super().__init__(ea_output_dir, stage, run_name, whitelist)

    def _generate_mq5(self, yaml_path: Path) -> Path:
        """Render and write the conformation EA, using trigger-optimised parameters.

        param yaml_path: Path to the indicator YAML
        return: Path to written .mq5 file
        """

        # Load conformation indicator (to be optimised in this stage)
        conf_indicator_name, conf_indicator_data = load_indicator_data(yaml_path)

        # Render the EA code using the template and both indicators' data
        rendered = render_conformation_ea(
            self.template,
            conf_indicator_name,
            conf_indicator_data,
            trigger_indicator_data,
            symbols_array=self.whitelist
        )

        # Write the rendered EA code to the output .mq5 file
        output_file = self.ea_output_dir / f"{yaml_path.stem}.mq5"
        with open(output_file, "w") as f:
            f.write(rendered)

        return output_file


def render_conformation_ea(template: Template, conf_indi_name: str, conf_indi_data: dict,
                           trigger_indi_data: dict, symbols_array: list) -> str:
    """Render MQL5 code for conformation EA stage (two indicators).

    param template: Jinja2 template for the EA
    param conf_indi_name: Name of the conformation indicator
    param conf_indi_data: Dict of conformation indicator properties
    param trigger_indi_data: Dict of trigger indicator result data
    return: Rendered MQL5 code as string
    """
    # Load optimised result for the trigger indicator (from previous pipeline stage)
    trigger_stage = get_stage("Trigger")
    trigger_indicator_name, trigger_indicator_data = load_results_data(self.run_name, trigger_stage)

    # Extract base conditions for the conformation indicator (long and short)
    conf_long_full = conf_indi_data.get("base_conditions", {}).get("long", "")
    conf_short_full = conf_indi_data.get("base_conditions", {}).get("short", "")

    # Prepare context for the template render call
    return template.render(
        enum_definitions=build_enum_definitions(conf_indi_data, trigger_indi_data),
        symbols_array=symbols_array,

        # Conformation indicator (to be optimised)
        conf_indicator_name=conf_indi_name,
        conf_input_lines=build_input_lines(conf_indi_data),
        conf_indicator_path=conf_indi_data["indicator_path"],  # Path to indicator .ex5 or .mq5
        conf_inputs=[k for k in conf_indi_data.get("inputs", {})],  # List of input variable names
        conf_buffers=conf_indi_data.get("buffers", []),  # List of buffer indices or names
        conf_long_conditions=extract_conformation_conditions(conf_long_full),
        conf_short_conditions=extract_conformation_conditions(conf_short_full),

        # Trigger settings (fixed indicator):
        trigger_path=trigger_indi_data["indicator_path"],
        trigger_inputs=[v["default"] for v in trigger_indi_data["inputs"].values()],
        trigger_buffers=trigger_indi_data.get("buffers", []),
        trigger_long_conditions=trigger_indi_data["base_conditions"]["long"],
        trigger_short_conditions=trigger_indi_data["base_conditions"]["short"],
    )


def extract_conformation_conditions(cond: str) -> str:
    """Extract the part of the condition before '&&' for conformation logic.

    param cond: The full condition string
    return: The condition before '&&', stripped of whitespace
    """
    # Only use the first condition (before the '&&'), or return the whole string if '&&' not present
    return cond.split('&&')[0].strip() if cond else cond
