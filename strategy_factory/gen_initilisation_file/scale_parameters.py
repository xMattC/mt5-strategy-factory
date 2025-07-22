import logging

logger = logging.getLogger(__name__)


def scale_parameters(
        param_dict: dict,
        max_total_iterations: int,
        per_param: bool = False,
        even_spacing: bool = True,
        allow_step_reduction: bool = False):
    """ Scale input parameter ranges to keep total combinations under a max limit.

    param param_dict: Dict of {param_name: {default, min, max, step, optimize, type}}
    param max_total_iterations: Max combinations (total or per parameter, depending on per_param)
    param per_param: If True, applies the limit to each param individually, else to the full grid
    param even_spacing: If True, always space parameter values evenly (like linspace); else, use legal steps as much as possible
    return: List of (param_name, scaled_param_dict)
    """
    from functools import reduce
    from operator import mul

    optimisable = []
    for name, param in param_dict.items():
        if not param.get("optimize", True):
            continue
        start = float(param.get("min", param["default"]))
        end = float(param.get("max", param["default"]))
        step = float(param.get("step", 1))
        dtype = param.get("type", "float")
        count = max(1, int(round((end - start) / step)) + 1)
        optimisable.append(
            {
                "name": name,
                "start": start,
                "end": end,
                "step": step,
                "default": param["default"],
                "count": count,
                "type": dtype
            }
        )

    if per_param:
        for p in optimisable:
            if p["count"] > max_total_iterations or allow_step_reduction:
                N = min(p["count"], int(max_total_iterations)) if not allow_step_reduction else int(
                    max_total_iterations)
                span = p["end"] - p["start"]

                if even_spacing:
                    raw_step = span / (N - 1) if N > 1 else span
                    p["step"] = max(1, int(round(raw_step))) if p["type"] == "int" else raw_step
                else:
                    raw_step = span / (N - 1) if N > 1 else span
                    p["step"] = max(1, int(round(raw_step))) if p["type"] == "int" else raw_step
    else:
        total = reduce(mul, (p["count"] for p in optimisable), 1)
        if total > max_total_iterations or allow_step_reduction:
            scale_factor = (total / max_total_iterations) ** (1 / len(optimisable))
            for p in optimisable:
                new_count = p["count"] / scale_factor if scale_factor != 0 else 1
                span = p["end"] - p["start"]
                raw_step = span / new_count if new_count > 1 else span
                p["step"] = max(1, int(round(raw_step))) if p["type"] == "int" else raw_step

    result = []
    for name, param in param_dict.items():
        if param.get("optimize", True):
            match = next(p for p in optimisable if p["name"] == name)
            param = {
                "default": param["default"],
                "min": match["start"],
                "max": match["end"],
                "step": match["step"],
                "optimize": True,
                "type": match["type"]
            }
        result.append((name, param))
    return result


# --- Helper: print grid values for each parameter ---
def print_param_grid(param):
    min_v = param["min"]
    max_v = param["max"]
    step = param["step"]
    dtype = param.get("type", "float")
    if step == 0:
        values = [min_v]
    else:
        N = int(round((max_v - min_v) / step)) + 1
        values = []
        for i in range(N):
            v = min_v + i * step
            if v > max_v + 1e-9:
                break
            values.append(int(round(v)) if dtype == "int" else round(v, 6))
        # Ensure max is always included
        if (dtype == "int" and int(round(max_v)) not in values) or (dtype != "int" and abs(values[-1] - max_v) > 1e-9):
            values.append(int(round(max_v)) if dtype == "int" else round(max_v, 6))
    print(f"    Values: {values}")


# --- Example usage ---
if __name__ == "__main__":
    ini_lines = {
        "InpPeriod": {"default": 9, "min": 1, "max": 50, "step": 1, "optimize": True, "type": "int"},
        "InpPeriodSm": {"default": 1, "min": 1, "max": 10, "step": 1, "optimize": True, "type": "float"},
        "inp_force_opt": {"default": 1, "min": 1, "max": 2, "step": 1, "optimize": True, "type": "int"}
    }

    print("=== Per param, at most 5 values, even spacing, respecting type ===")
    result = scale_parameters(ini_lines, max_total_iterations=5, per_param=True, even_spacing=True)
    for name, param in result:
        print(name, param)
        print_param_grid(param)

    print("\n=== Per param, at most 5 values, original step multiples ===")
    result = scale_parameters(ini_lines, max_total_iterations=5, per_param=True, even_spacing=False)
    for name, param in result:
        print(name, param)
        print_param_grid(param)

    print("\n=== Cap full grid (product) at 10 total combinations, even spacing ===")
    result = scale_parameters(ini_lines, max_total_iterations=10, per_param=False, even_spacing=True)
    for name, param in result:
        print(name, param)
        print_param_grid(param)
