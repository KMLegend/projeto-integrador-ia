from application.dto.dataset_summary import DatasetSummary
from application.ports.dataset_catalog import DatasetCatalog


class RegisterDataset:
    """Caso de uso: validar e registrar um dataset CSV enviado pelo usuario."""

    def __init__(self, catalog: DatasetCatalog) -> None:
        self._catalog = catalog

    def execute(self, reference: str, content: str) -> DatasetSummary:
        return self._catalog.register(reference, content)
