from enum import StrEnum


class StockRiskLevel(StrEnum):
    """Niveis de risco de estoque definidos na regra RN-06."""

    SHORTAGE = "SHORTAGE"
    ADEQUATE = "ADEQUATE"
    EXCESS = "EXCESS"

    def label_pt_br(self) -> str:
        labels = {
            StockRiskLevel.SHORTAGE: "Possível falta",
            StockRiskLevel.ADEQUATE: "Adequado",
            StockRiskLevel.EXCESS: "Possível excesso",
        }
        return labels[self]
