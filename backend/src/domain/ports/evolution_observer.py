from typing import Protocol

from domain.evolution.generation_report import GenerationReport


class EvolutionObserver(Protocol):
    """Porta para observacao do progresso de geracoes da evolucao."""

    def on_generation(self, report: GenerationReport) -> None:
        """Chamado a cada geracao avaliada com o relatorio de convergencia."""
        ...
