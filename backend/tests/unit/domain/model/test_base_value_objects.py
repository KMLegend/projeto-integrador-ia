from decimal import Decimal
import pytest

from domain.errors.domain_errors import (
    EmptyPositionError,
    InvalidMoneyError,
    InvalidPercentageError,
    InvalidPositionError,
    InvalidSkuError,
    NegativeMoneyError,
    NegativeQuantityError,
)
from domain.model.fitness_score import FitnessScore
from domain.model.money import Money
from domain.model.percentage import Percentage
from domain.model.position import MaybePosition, Position
from domain.model.quantity import Quantity
from domain.model.sku import Sku
from domain.model.unit_price import UnitPrice


def test_money_from_reais_and_multiplication() -> None:
    m = Money.from_reais("18.78")
    result = m.times(22)
    expected = Money.from_reais("413.16")
    assert result == expected
    assert result.value_for_serialization() == "413.16"


def test_money_rejects_float() -> None:
    with pytest.raises(InvalidMoneyError):
        Money.from_reais(18.78)  # type: ignore[arg-type]


def test_money_from_decimal() -> None:
    m = Money.from_reais(Decimal("100.50"))
    assert m.value_for_serialization() == "100.50"


def test_money_arithmetic_and_predicates() -> None:
    m1 = Money.from_reais("50.00")
    m2 = Money.from_reais("30.00")
    assert m1.plus(m2) == Money.from_reais("80.00")
    assert m1.minus(m2) == Money.from_reais("20.00")
    assert m1.is_greater_than(m2)
    assert not m2.is_greater_than(m1)
    assert not m1.is_zero()
    assert Money.zero().is_zero()

    with pytest.raises(NegativeMoneyError):
        m2.minus(m1)


def test_quantity_operations_and_invariants() -> None:
    q1 = Quantity.of(10)
    q2 = Quantity.of(4)
    assert q1.plus(q2) == Quantity.of(14)
    assert q1.minus(q2) == Quantity.of(6)
    assert q2.minus(q1) == Quantity.zero()
    assert q1.limited_to(Quantity.of(5)) == Quantity.of(5)
    assert q1.decremented() == Quantity.of(9)
    assert Quantity.zero().decremented() == Quantity.zero()

    with pytest.raises(NegativeQuantityError):
        Quantity.of(-1)


def test_unit_price_computations() -> None:
    price = UnitPrice.from_reais("18.78")
    quantity = Quantity.of(22)
    total = price.total_for(quantity)
    assert total == Money.from_reais("413.16")

    cheaper = UnitPrice.from_reais("5.86")
    assert price.is_more_expensive_than(cheaper)
    assert not cheaper.is_more_expensive_than(price)


def test_sku_validation() -> None:
    sku = Sku("CAFE-500G")
    assert sku.value_for_serialization() == "CAFE-500G"
    assert sku.matches(Sku("CAFE-500G"))
    assert not sku.matches(Sku("LEITE-UHT-1L"))

    with pytest.raises(InvalidSkuError):
        Sku("")
    with pytest.raises(InvalidSkuError):
        Sku("   ")


def test_percentage_calculations() -> None:
    p = Percentage.of(Quantity.of(120), Quantity.of(146))
    assert pytest.approx(p.points(), abs=1e-4) == 82.19178
    assert p.times_weight(10.0) == pytest.approx(821.9178, abs=1e-4)

    assert Percentage.of(Quantity.of(0), Quantity.of(0)) == Percentage.hundred()
    assert Percentage.zero().points() == 0.0

    with pytest.raises(InvalidPercentageError):
        Percentage(-5.0)


def test_fitness_score_ordering() -> None:
    f1 = FitnessScore(816.92)
    f2 = FitnessScore(236.58)
    assert f1.is_better_than(f2)
    assert f1 > f2
    assert f2 < f1
    assert f1.value_for_serialization() == 816.92


def test_position_and_maybe_position() -> None:
    pos = Position(3)
    assert pos.index_value() == 3
    assert pos.value_for_serialization() == 3

    with pytest.raises(InvalidPositionError):
        Position(-1)

    maybe_present = pos.as_maybe()
    assert maybe_present.is_present()
    assert not maybe_present.is_absent()
    assert maybe_present.value() == pos

    maybe_absent = MaybePosition.absent()
    assert maybe_absent.is_absent()
    assert not maybe_absent.is_present()
    with pytest.raises(EmptyPositionError):
        maybe_absent.value()
