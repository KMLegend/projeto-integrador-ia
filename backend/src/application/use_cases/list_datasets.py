from application.dto.dataset_summary import DatasetSummary
from application.ports.dataset_catalog import DatasetCatalog


class ListDatasets:
    """Caso de uso: listar os datasets disponiveis para otimizacao."""

    def __init__(self, catalog: DatasetCatalog) -> None:
        self._catalog = catalog

    def execute(self) -> tuple[DatasetSummary, ...]:
        return self._catalog.list_all()

    def required_columns(self) -> tuple[str, ...]:
        return self._catalog.required_columns()
