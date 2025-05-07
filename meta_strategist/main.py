from meta_strategist.pipeline.stages import get_stage
from meta_strategist.generators.ini_generator import IniConfig
from meta_strategist.pipeline.optimisation import Optimization

if __name__ == "__main__":
    CONFIG = IniConfig(
        run_name='Apollo',
        start_date="2023.01.01",
        end_date="2023.12.31",
        period="D1",
        custom_criteria="ProfitFactor",
        symbol_mode="ALL",
        data_split="year",
        risk=0.02,
        sl=2,
        tp=1
    )

    STAGE = get_stage("Trigger")

    pipeline = Optimization(config=CONFIG, stage=STAGE)
    pipeline.run_optimisation()
