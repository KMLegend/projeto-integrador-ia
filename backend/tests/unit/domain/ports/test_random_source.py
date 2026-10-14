import pytest

from infrastructure.randomness.seeded_random_source import SeededRandomSource
from tests.doubles.scripted_random_source import ScriptedRandomSource


def test_seeded_random_source_determinism_across_runs() -> None:
    sequences = []
    for _ in range(10):
        src = SeededRandomSource(42)
        seq = [src.ratio() for _ in range(20)] + [src.integer_inclusive(1, 100) for _ in range(20)]
        sequences.append(seq)

    # Todas as 10 execucoes devem ser exatamente iguais
    for i in range(1, 10):
        assert sequences[i] == sequences[0]


def test_scripted_random_source_exhaustion_error() -> None:
    scripted = ScriptedRandomSource(ratios=[0.1, 0.5], integers=[10])

    assert scripted.ratio() == 0.1
    assert scripted.ratio() == 0.5
    with pytest.raises(RuntimeError, match="ratios esgotada"):
        scripted.ratio()

    assert scripted.integer_inclusive(0, 10) == 10
    with pytest.raises(RuntimeError, match="inteiros esgotada"):
        scripted.integer_inclusive(0, 10)
