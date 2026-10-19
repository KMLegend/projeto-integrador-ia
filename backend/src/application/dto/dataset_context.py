from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class DatasetContext:
    """Metadados do dataset usados na apresentacao do resultado."""

    model_mae: float = 0.0
    product_names: dict[str, str] = field(default_factory=dict)

    def name_for(self, sku: str) -> str:
        return self.product_names.get(sku, sku)
