from domain.model.quantity import Quantity
from domain.model.stock_risk_level import StockRiskLevel
from domain.policy.stock_risk_classifier import StockRiskClassifier


def test_shortage_detection() -> None:
    classifier = StockRiskClassifier.standard()
    # Estoque menor que a previsao: ex. 40 < 50
    level = classifier.classify(Quantity.of(40), Quantity.of(50))
    assert level == StockRiskLevel.SHORTAGE


def test_excess_detection() -> None:
    classifier = StockRiskClassifier.standard()
    # 50 * 1.8 = 90. Estoque 91 > 90 -> EXCESS
    level = classifier.classify(Quantity.of(91), Quantity.of(50))
    assert level == StockRiskLevel.EXCESS


def test_exact_boundary_stock_equals_forecast() -> None:
    classifier = StockRiskClassifier.standard()
    # 50 == 50 -> ADEQUATE
    level = classifier.classify(Quantity.of(50), Quantity.of(50))
    assert level == StockRiskLevel.ADEQUATE


def test_exact_boundary_stock_equals_threshold() -> None:
    classifier = StockRiskClassifier.standard()
    # 50 * 1.8 = 90. Estoque 90 == 90 -> ADEQUATE (nao excede estritamente)
    level = classifier.classify(Quantity.of(90), Quantity.of(50))
    assert level == StockRiskLevel.ADEQUATE


def test_adequate_middle_range() -> None:
    classifier = StockRiskClassifier.standard()
    # 70 unidades entre 50 e 90 -> ADEQUATE
    level = classifier.classify(Quantity.of(70), Quantity.of(50))
    assert level == StockRiskLevel.ADEQUATE
