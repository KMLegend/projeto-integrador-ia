from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DatasetSummary:
    """Resumo de um dataset disponivel para otimizacao.

    OC-8: DTO de borda com campos primitivos, traduzido para JSON na API.
    """

    reference: str
    rows: int
    skus: int
    uploaded_at: str
    is_builtin: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "reference": self.reference,
            "rows": self.rows,
            "skus": self.skus,
            "uploaded_at": self.uploaded_at,
            "is_builtin": self.is_builtin,
        }
