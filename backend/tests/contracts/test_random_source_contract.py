import pytest

from domain.ports.random_source import RandomSource
from infrastructure.randomness.seeded_random_source import SeededRandomSource
from tests.doubles.scripted_random_source import ScriptedRandomSource


@pytest.mark.parametrize("source_impl", [
    SeededRandomSource(42),
    ScriptedRandomSource(ratios=[0.1, 0.4, 0.9], integers=[3, 7, 15]),
])
def test_random_source_contract_methods(source_impl: RandomSource) -> None:
    ratio = source_impl.ratio()
    assert 0.0 <= ratio < 1.0

    below = source_impl.integer_below(10)
    assert 0 <= below < 10

    inclusive = source_impl.integer_inclusive(5, 20)
    assert 5 <= inclusive <= 20
