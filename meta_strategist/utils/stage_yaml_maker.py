from pathlib import Path
import yaml


def get_output_yaml_path(run_dir: Path, phase: str) -> Path:
    # Output: run_dir / outputs / Trigger / the_trigger.yaml
    phase_cap = phase.capitalize()
    out_dir = run_dir / phase_cap
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"the_{phase.lower()}.yaml"


def create_stage_yaml(run_dir: Path, phase: str, indicator: str, out_filename: Path = None):
    # Always get indicators from the meta-strategist-private/indicators folder (two levels up from utils)
    indicators_dir = Path(__file__).resolve().parents[2] / "indicators"
    indicator_lc = indicator.lower()
    match = None
    for y in indicators_dir.glob("*.yaml"):
        with open(y, "r") as f:
            data = yaml.safe_load(f)
        top_key = next(iter(data)).lower()
        if top_key == indicator_lc:
            match = y
            break
    if not match:
        raise FileNotFoundError(f"No YAML found for indicator '{indicator}' in {indicators_dir}")
    with open(match, "r") as f:
        indi_data = yaml.safe_load(f)
    indicator_name = next(iter(indi_data))
    indi_section = indi_data[indicator_name]

    # Only take the default values for all input parameters
    inputs = indi_section.get("inputs", {})
    minimal = {k: v["default"] for k, v in inputs.items() if "default" in v}

    out_path = out_filename or get_output_yaml_path(run_dir, phase)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists():
        print(f"YAML file already exists: {out_path}\nPlease delete it if you need to remake.")
        return

    with open(out_path, "w") as f:
        yaml.dump({indicator_name: minimal}, f, sort_keys=False, indent=2)
    print(f"Stage YAML created: {out_path}")



def maker(phase: str, indicator: str, run_dir: Path = None):
    """
    Convenience entry point to be called from a wrapper script.
    phase: e.g., 'trigger', 'conformation', etc.
    indicator: e.g., 'aroon', 'aso', etc.
    run_dir: The root dir for this run (default = where script is called from)
    """
    if run_dir is None:
        run_dir = Path(__file__).parent.resolve()
    create_stage_yaml(run_dir, phase, indicator)
