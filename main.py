from pathlib import Path

# Optimization settings for RSI
RSI_OPT_SETTINGS = {
    "default": 14,
    "min": 2,
    "max": 50,
    "step": 1
}

# Output .set file
TEMPLATE_PATH = Path("base_rsi.set")
OUTPUT_DIR = Path("generated_sets")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "RSI_Optimization.set"


def generate_optimization_set_file():
    """Generates a single .set file with optimization settings for RSI."""
    with open(TEMPLATE_PATH, "r") as f:
        content = f.read()

    # Replace with default value and optimization string
    content = content.replace("__RSI_PERIOD__", str(RSI_OPT_SETTINGS["default"]))
    optinfo = f"1|{RSI_OPT_SETTINGS['min']}|{RSI_OPT_SETTINGS['max']}|{RSI_OPT_SETTINGS['step']}|Y"
    content = content.replace("__RSI_PERIOD_OPTINFO__", optinfo)

    with open(OUTPUT_FILE, "w") as f:
        f.write(content)

    print(f"Generated optimization .set file: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_optimization_set_file()
