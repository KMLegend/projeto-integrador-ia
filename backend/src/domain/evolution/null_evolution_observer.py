from dataclasses import dataclass

from domain.evolution.generation_report import GenerationReport


@dataclass(frozen=True, slots=True)
class NullEvolutionObserver:
    """Implementacao Null Object para observador de evolucao (evita checagem de None)."""

    def on_generation(self, report: GenerationReport) -> None:
        pass
