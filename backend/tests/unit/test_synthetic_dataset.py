from domain.ports.stock_history_repository import StockHistoryRepository
from infrastructure.dataset.product_catalog import BASE_CATALOG
from infrastructure.dataset.simulated_stock_history_repository import SimulatedStockHistoryRepository
from infrastructure.dataset.synthetic_dataset_generator import SyntheticDatasetGenerator


def test_generator_produces_120_records_for_base_catalog() -> None:
    generator = SyntheticDatasetGenerator(seed=42)
    snapshots = generator.generate()

    assert snapshots.size() == 120
    assert len(BASE_CATALOG) == 6


def test_generator_is_deterministic_with_same_seed() -> None:
    gen1 = SyntheticDatasetGenerator(seed=42)
    gen2 = SyntheticDatasetGenerator(seed=42)

    snaps1 = gen1.generate()
    snaps2 = gen2.generate()

    assert snaps1.features_matrix_rows() == snaps2.features_matrix_rows()
    assert snaps1.target_vector() == snaps2.target_vector()


def test_latest_per_product_matches_canonical_reference_values() -> None:
    generator = SyntheticDatasetGenerator(seed=42)
    snapshots = generator.generate()
    latest = snapshots.latest_per_product()

    assert latest.size() == 6

    expected_values = {
        "Arroz 5kg": (201, 29.89),
        "Café 500g": (192, 18.78),
        "Detergente 500ml": (202, 3.07),
        "Feijão 1kg": (270, 9.55),
        "Leite UHT 1L": (226, 5.86),
        "Refrigerante 2L": (263, 10.76),
    }

    for snap in latest.snapshots():
        name = snap.product_name()
        assert name in expected_values
        exp_soh, exp_price = expected_values[name]
        assert snap.stock_on_hand() == exp_soh
        assert snap.unit_price_float() == exp_price


def test_simulated_stock_history_repository_implements_protocol() -> None:
    repo: StockHistoryRepository = SimulatedStockHistoryRepository()
    snapshots = repo.load_history()

    assert snapshots.size() == 120
