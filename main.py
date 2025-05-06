from src.stages import get_stage
from src.ini_generator import IniConfig
from src.optimisation_pipeline import OptimizationPipeline


if __name__ == "__main__":
    CONFIG = IniConfig(
        run_name='Apollo',
        start_date="2023.01.01",
        end_date="2023.12.31",
        period="H1",
        custom_criteria="ProfitFactor",
        symbol_mode="ALL",
        data_split="year",
        risk=0.01,
        sl=50,
        tp=100
    )
    STAGE = get_stage("C1")

    pipeline = OptimizationPipeline(CONFIG, STAGE)
    pipeline.run_optimisation()
