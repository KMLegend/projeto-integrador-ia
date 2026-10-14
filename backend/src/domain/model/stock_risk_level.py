from enum import StrEnum


class StockRiskLevel(StrEnum):
    """Niveis de risco de estoque definidos na regra RN-06."""

    SHORTAGE = "SHORTAGE"
    ADEQUATE = "ADEQUATE"
    EXCESS = "EXCESS"

    def label_pt_br(self) -> str:
        return _LABELS_PT_BR[self]


_LABELS_PT_BR: dict[StockRiskLevel, str] = {
    StockRiskLevel.SHORTAGE: "Possível falta",
    StockRiskLevel.ADEQUATE: "Adequado",
    StockRiskLevel.EXCESS: "Possível excesso",
}
