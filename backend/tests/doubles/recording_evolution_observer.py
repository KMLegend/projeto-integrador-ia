from domain.evolution.generation_report import GenerationReport
from domain.ports.evolution_observer import EvolutionObserver


class RecordingEvolutionObserver(EvolutionObserver):
    """Duble de EvolutionObserver que armazena todos os relatorios de geracao em memoria."""

    def __init__(self) -> None:
        self._reports: list[GenerationReport] = []

    def on_generation(self, report: GenerationReport) -> None:
        self._reports.append(report)

    def reports(self) -> tuple[GenerationReport, ...]:
        return tuple(self._reports)

    def reports_count(self) -> int:
        return len(self._reports)

    def last_report(self) -> GenerationReport | None:
        if not self._reports:
            return None
        return self._reports[-1]
