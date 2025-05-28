import math
from functools import reduce
from operator import mul
import logging

logger = logging.getLogger(__name__)


def scale_parameters(param_dict: dict, max_total_iterations: int, mode: int = 0):
    """Scale input parameter ranges to keep total combinations under a max limit.

    param param_dict: Dict of {param_name: {default, min, max, step, optimize}}
    return: List of (param_name, scaled_param_dict)
    """
    import math
    from functools import reduce
    from operator import mul

    # Extract optimisable parameters only
    optimisable = []
    for name, param in param_dict.items():
        if not param.get("optimize", True):
            continue
        start = float(param.get("min", param["default"]))
        end = float(param.get("max", param["default"]))
        step = float(param.get("step", 1))
        count = max(1, math.floor((end - start) / step) + 1)
        optimisable.append({"name": name, "start": start, "end": end, "step": step, "default": param["default"], "count": count})

    total = reduce(mul, (p["count"] for p in optimisable), 1)

    if total > max_total_iterations:
        scale_factor = (total / max_total_iterations) ** (1 / len(optimisable))
        for p in optimisable:
            new_count = p["count"] / scale_factor
            p["step"] = max(1, int(math.ceil((p["end"] - p["start"]) / new_count)))

    # Update param_dict with scaled step
    result = []
    for name, param in param_dict.items():
        if param.get("optimize", True):
            match = next(p for p in optimisable if p["name"] == name)
            param = {
                "default": param["default"],
                "min": match["start"],
                "max": match["end"],
                "step": match["step"],
                "optimize": True
            }
        result.append((name, param))

    return result


# Example usage
if __name__ == "__main__":
    ini_lines = [
        "InpPeriod = 9||1||1||50||Y",
        "InpPeriodSm = 1||1||1||10||Y",
        "inp_force_opt = 1||1||1||2||N"
    ]

    logger.info("=== Proportional Scaling ===")
    result_proportional = scale_parameters(ini_lines, max_total_iterations=100, mode=0)
    # for line in result_proportional:
    #     print(line)

    print(result_proportional)
    logger.info("\n=== Even Scaling ===")
    result_even = scale_parameters(ini_lines, max_total_iterations=100, mode=1)
    # for line in result_even:
    #     print(line)
