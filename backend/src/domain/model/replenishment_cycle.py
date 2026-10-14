from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.errors.domain_errors import InvalidCycleError
from domain.model.quantity import Quantity

if TYPE_CHECKING:
    from domain.forecasting.weekly_demand_forecast import WeeklyDemandForecast


@dataclass(frozen=True, slots=True)
class ReplenishmentCycle:
    """Ciclo de reposicao de compras (RN-01)."""

    _weeks: int

    def __post_init__(self) -> None:
        is_invalid_type = isinstance(self._weeks, bool) or not isinstance(self._weeks, int)
        if is_invalid_type or self._weeks < 1:
            raise InvalidCycleError(
                f"Ciclo de reposicao deve ser de pelo menos 1 semana: {self._weeks}"
            )

    @staticmethod
    def default() -> "ReplenishmentCycle":
        return ReplenishmentCycle(4)

    @staticmethod
    def of_weeks(weeks: int) -> "ReplenishmentCycle":
        return ReplenishmentCycle(weeks)

    def weeks_count(self) -> int:
        return self._weeks

    def demand_for(self, forecast: "WeeklyDemandForecast") -> Quantity:
        return Quantity(forecast.units_value() * self._weeks)

    def value_for_serialization(self) -> int:
        return self._weeks
