from application.use_cases.build_replenishment_scenario import BuildReplenishmentScenario
from domain.model.replenishment_cycle import ReplenishmentCycle
from infrastructure.dataset.simulated_stock_history_repository import (
    SimulatedStockHistoryRepository,
)
from tests.doubles.fixed_demand_forecaster import FixedDemandForecaster


def test_build_replenishment_scenario_produces_exact_canonical_needs() -> None:
    repository = SimulatedStockHistoryRepository()
    forecaster = FixedDemandForecaster(
        {
            "ARROZ-5KG": 42,
            "CAFE-500G": 60,
            "DETERGENTE-500ML": 39,
            "FEIJAO-1KG": 46,
            "LEITE-UHT-1L": 81,
            "REFRIGERANTE-2L": 65,
        }
    )

    use_case = BuildReplenishmentScenario(repository, forecaster)
    scenario = use_case.execute(ReplenishmentCycle.default())

    assert scenario.size() == 6
    assert scenario.required_total().units_value() == 146

    # Ordem alfabetica dos itens
    expected_quantities = (0, 48, 0, 0, 98, 0)
    for idx, expected_qty in enumerate(expected_quantities):
        assert scenario.required_quantities()[idx].units_value() == expected_qty

    # Custo total da necessidade plena = 48 * 18.78 + 98 * 5.86 = 901.44 + 574.28 = 1475.72
    assert scenario.total_required_cost().value_for_serialization() == "1475.72"
