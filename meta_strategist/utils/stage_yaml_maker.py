from pathlib import Path
import yaml
from meta_strategist.optimise import Stage


def get_output_yaml_path(run_dir: Path, phase: str) -> Path:
    """Get the output YAML file path for a given run and phase.

    param run_dir: Root directory for the run
    param phase: Stage name (e.g., 'Trigger')
    return: Path to the output YAML file
    """
    # Output: run_dir / Trigger / the_trigger.yaml
    phase_cap = phase.capitalize()
    out_dir = run_dir / phase_cap
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"the_{phase.lower()}.yaml"


def find_indicator_yaml(indicators_dir: Path, indicator: str) -> Path:
    """Search for the YAML file matching the indicator name in the given directory.

    param indicators_dir: Directory containing indicator YAML files
    param indicator: Name of the indicator (case-insensitive)
    return: Path to the matching YAML file
    raises: FileNotFoundError if not found
    """
    indicator_lc = indicator.lower()
    for y in indicators_dir.glob("*.yaml"):
        with open(y, "r") as f:
            data = yaml.safe_load(f)
        top_key = next(iter(data)).lower()
        if top_key == indicator_lc:
            return y
    raise FileNotFoundError(f"No YAML found for indicator '{indicator}' in {indicators_dir}")


def extract_minimal_defaults(indicator_yaml: Path) -> tuple[str, dict]:
    """Extract only the default values for all input parameters from the indicator YAML.

    param indicator_yaml: Path to the indicator YAML file
    return: (indicator_name, dict of input defaults)
    """
    with open(indicator_yaml, "r") as f:
        indi_data = yaml.safe_load(f)
    indicator_name = next(iter(indi_data))
    indi_section = indi_data[indicator_name]
    inputs = indi_section.get("inputs", {})
    minimal = {k: v["default"] for k, v in inputs.items() if "default" in v}
    return indicator_name, minimal


def create_stage_yaml(run_dir: Path, stage: Stage, indicator: str, out_filename: Path = None):
    """Create a minimal stage YAML for a specific indicator and stage.

    param run_dir: Root directory for the run
    param stage: Stage object (determines indicator subdirectory)
    param indicator: Name of the indicator to use
    param out_filename: Optional custom output filename
    """
    # Determine the root indicators directory, and use the subdirectory for the stage if needed
    indicators_dir = Path(__file__).resolve().parents[2] / "indicators"
    if getattr(stage, "indi_dir", None):
        indicators_dir = indicators_dir / stage.indi_dir

    # Find the YAML file for the requested indicator
    indicator_yaml = find_indicator_yaml(indicators_dir, indicator)
    # Extract minimal input defaults
    indicator_name, minimal = extract_minimal_defaults(indicator_yaml)

    # Determine the output YAML file path (use custom if provided)
    out_path = out_filename or get_output_yaml_path(run_dir, stage.name)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Prevent overwrite unless the user deletes the old file
    if out_path.exists():
        print(f"YAML file already exists: {out_path}\nPlease delete it if you need to remake.")
        return

    # Write the minimal YAML (only defaults for inputs) to the output file
    with open(out_path, "w") as f:
        yaml.dump({indicator_name: minimal}, f, sort_keys=False, indent=2)
    print(f"Stage YAML created: {out_path}")


def maker(phase: str, indicator: str, run_dir: Path = None):
    """ Convenience entry point to be called from a wrapper script.

    param phase: Name of the stage (e.g., 'trigger', 'conformation')
    param indicator: Indicator name (e.g., 'aroon', 'aso')
    param run_dir: Root directory for this run (defaults to the script's directory)
    """
    from meta_strategist.optimise import get_stage  # Import get_stage inside the function
    if run_dir is None:
        run_dir = Path(__file__).parent.resolve()  # Use script location if not given
    stage = get_stage(phase.capitalize())  # Get the Stage object for this phase
    create_stage_yaml(run_dir, stage, indicator)
