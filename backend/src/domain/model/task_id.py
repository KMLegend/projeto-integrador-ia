from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskId:
    """Identificador opaco de tarefa assincrona."""

    _value: str

    @staticmethod
    def of(value: str) -> "TaskId":
        return TaskId(value)

    def value_for_serialization(self) -> str:
        return self._value
