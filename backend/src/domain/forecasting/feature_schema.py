class FeatureSchema:
    """Ordem normativa e unica das 5 features do modelo de regressao linear (Secao 2)."""

    SCHEMA_VERSION: str = "1.0"

    ORDERED_NAMES: tuple[str, ...] = (
        "stock_on_hand",
        "weekly_outflow",
        "monthly_outflow",
        "unit_price",
        "promotion_flag",
    )
