from meta_strategist.pipeline.stages import get_stage
from meta_strategist.generators.ini_generator import IniConfig
from meta_strategist.pipeline.optimisation import Optimization

if __name__ == "__main__":
    CONFIG = IniConfig(
        run_name='Apollo',
        start_date="2023.01.01",
        end_date="2023.12.31",
        period="D1",
        custom_criteria="2",
        symbol_mode="2",
        data_split="month",
        risk=2.0,
        sl=1,
        tp=1.5,
        max_iterations=200
    )

    STAGE = get_stage("Trigger")

    pipeline = Optimization(config=CONFIG, stage=STAGE)
    pipeline.run_optimisation()
