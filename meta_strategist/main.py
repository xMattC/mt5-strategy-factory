from meta_strategist.core.stages import get_stage
from meta_strategist.generators.ini_generator import IniConfig
from meta_strategist.core.optimisation_pipeline import OptimizationPipeline

CONFIG = IniConfig(
    run_name='Apollo',
    start_date="2023.01.01",
    end_date="2023.12.31",
    period="D1",
    custom_criteria="ProfitFactor",
    symbol_mode="ALL",
    data_split="year",
    risk=0.01,
    sl=50,
    tp=100
)
STAGE = get_stage("C1")


def main():
    pipeline = OptimizationPipeline(CONFIG, STAGE)
    pipeline.run_optimisation()


if __name__ == "__main__":
    main()
