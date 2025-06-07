import importlib


def load_all_pipeline_stages(pipeline_name: str):
    """ Dynamically import and return the STAGES list for the specified pipeline.

    param pipeline_name: The name of the pipeline (e.g., "trend_following")
    return: List of StageConfig objects for the pipeline
    raises RuntimeError: If the pipeline or STAGES cannot be found/imported
    """
    try:
        stages_module = importlib.import_module(f"meta_strategist.pipelines.{pipeline_name}.stages")
        return stages_module.STAGES

    except ImportError as e:
        raise RuntimeError(f"Could not import pipeline '{pipeline_name}': {e}")

    except AttributeError:
        raise RuntimeError(f"'STAGES' not defined in pipeline '{pipeline_name}'.")
