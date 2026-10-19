from pathlib import Path
from typing import Protocol

from application.dto.dataset_summary import DatasetSummary


class DatasetCatalog(Protocol):
    """Porta para registro e consulta de datasets de historico de estoque."""

    def register(self, reference: str, content: str) -> DatasetSummary:
        """Valida e persiste um dataset CSV sob a referencia informada."""
        ...

    def list_all(self) -> tuple[DatasetSummary, ...]:
        """Lista os datasets disponiveis, incluindo o embutido."""
        ...

    def path_for(self, reference: str) -> Path | None:
        """Caminho do arquivo da referencia, ou None se nao for um dataset carregado."""
        ...

    def required_columns(self) -> tuple[str, ...]:
        """Colunas obrigatorias que um CSV precisa ter para ser aceito."""
        ...
