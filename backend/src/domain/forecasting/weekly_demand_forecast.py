from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

from domain.errors.domain_errors import DomainError


class InvalidForecastError(DomainError):
    """Lancado quando a previsao semanal e menor que 1 (RN-02)."""


@dataclass(frozen=True, slots=True)
class WeeklyDemandForecast:
    """Demanda semanal prevista por produto, normalizada e >= 1 (RN-02)."""

    _units: int

    def __post_init__(self) -> None:
        if isinstance(self._units, bool) or not isinstance(self._units, int) or self._units < 1:
            raise InvalidForecastError(f"Previsao de demanda semanal deve ser >= 1: {self._units}")

    @staticmethod
    def of(units: int) -> "WeeklyDemandForecast":
        return WeeklyDemandForecast(units)

    @staticmethod
    def from_prediction(prediction: float) -> "WeeklyDemandForecast":
        d = Decimal(str(prediction))
        rounded = int(d.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))
        return WeeklyDemandForecast(max(1, rounded))

    def units_value(self) -> int:
        return self._units

    def value_for_serialization(self) -> int:
        return self._units
