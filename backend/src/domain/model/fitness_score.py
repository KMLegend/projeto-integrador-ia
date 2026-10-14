from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FitnessScore:
    _value: float

    def is_better_than(self, other: "FitnessScore") -> bool:
        return self._value > other._value

    def value(self) -> float:
        return self._value

    def value_for_serialization(self) -> float:
        return round(self._value, 2)

    def __lt__(self, other: "FitnessScore") -> bool:
        return self._value < other._value

    def __gt__(self, other: "FitnessScore") -> bool:
        return self._value > other._value
