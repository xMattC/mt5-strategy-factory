from meta_strategist.generators.ini_generator import _build_tester_inputs, IniConfig


def test_max_iterations_scaling_affects_step_size():
    inputs = {
        "test_param": {
            "default": 10,
            "min": 1,
            "max": 100,
            "step": 1,
            "optimize": True
        }
    }

    config = IniConfig(
        run_name="test",
        start_date="2023.01.01",
        end_date="2023.12.31",
        period="M5",
        custom_criteria="0",
        symbol_mode="0",
        data_split="none",
        risk=1.0,
        sl=10.0,
        tp=20.0,
        max_iterations=10
    )

    tester_inputs = _build_tester_inputs(config, inputs, in_sample=True, optimized_parameters=None)

    assert "test_param" in tester_inputs, "Parameter was not included in tester_inputs"

    value = tester_inputs["test_param"]
    parts = value.split("||")
    scaled_step = float(parts[2])

    assert scaled_step > 1, f"Step size was not scaled up: {scaled_step}"
    assert parts[-1] == "Y"
    assert int(float(parts[1])) == 1 and int(float(parts[3])) == 100
