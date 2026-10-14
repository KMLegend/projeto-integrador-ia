from dataclasses import dataclass

from domain.evolution.generation_report import GenerationReport
from domain.ports.evolution_observer import EvolutionObserver


@dataclass(frozen=True, slots=True)
class ThrottleConfig:  # OC-8: Agrupamento de parametros de throttle
    """Configuracao do throttle de relatorios de evolucao."""

    target_generations: int
    every: int = 10

    def should_emit(self, generation: int) -> bool:
        if generation == 0:
            return True
        if generation == self.target_generations - 1:
            return True
        return generation % self.every == 0


class ThrottledEvolutionObserver(EvolutionObserver):
    """Decorator de EvolutionObserver que filtra relatorios a cada N geracoes.

    Regra de aceite: sempre inclui a primeira geracao (0) e a ultima (target_generations - 1).
    """

    def __init__(
        self,
        inner: EvolutionObserver,
        config: ThrottleConfig,
    ) -> None:
        self._inner = inner
        self._config = config

    def on_generation(self, report: GenerationReport) -> None:
        if self._config.should_emit(report.generation_number()):
            self._inner.on_generation(report)
