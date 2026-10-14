from typing import Protocol

from domain.ports.evolution_observer import EvolutionObserver


class ProgressPublisher(EvolutionObserver, Protocol):
    """Porta para publicacao de eventos e estado terminal de progresso."""

    def publish_terminal_state(
        self,
        status: str,
        generation: int = -1,
        max_fitness: float = 0.0,
    ) -> None:
        """Publica mensagem de estado terminal no canal de progresso."""
        ...
