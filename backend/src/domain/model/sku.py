from dataclasses import dataclass

from domain.errors.domain_errors import InvalidSkuError


@dataclass(frozen=True, slots=True)
class Sku:
    _value: str

    def __post_init__(self) -> None:
        if not isinstance(self._value, str) or not self._value.strip():
            raise InvalidSkuError("SKU deve ser uma string nao vazia")

    def matches(self, other: "Sku") -> bool:
        return self._value == other._value

    def value_for_serialization(self) -> str:
        return self._value
