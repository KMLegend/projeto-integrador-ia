import pytest

from domain.errors.domain_errors import InvalidDatasetError
from infrastructure.dataset.csv_dataset_schema import CsvDatasetSchema
from infrastructure.dataset.csv_stock_history_repository import CsvStockHistoryRepository
from infrastructure.dataset.filesystem_dataset_catalog import FilesystemDatasetCatalog

HEADER = (
    "reference_date,sku,product,stock_on_hand,weekly_outflow,"
    "monthly_outflow,unit_price,promotion_flag,future_demand"
)
LINHA_A = "2026-01-05,CAFE-500G,Café 500g,192,60,240,18.78,0,60"
LINHA_B = "2026-01-05,LEITE-1L,Leite UHT 1L,226,81,324,5.86,1,81"
CSV_VALIDO = f"{HEADER}\n{LINHA_A}\n{LINHA_B}\n"


def test_parse_valido_produz_snapshots() -> None:
    snapshots = CsvDatasetSchema.parse(CSV_VALIDO)
    assert len(snapshots) == 2
    assert snapshots[0].product_name() == "Café 500g"
    assert snapshots[0].features() == (192.0, 60.0, 240.0, 18.78, 0.0)
    assert snapshots[1].future_demand() == 81


def test_coluna_extra_e_aceita() -> None:
    texto = f"{HEADER},category\n{LINHA_A},Mercearia\n"
    assert len(CsvDatasetSchema.parse(texto)) == 1


def test_coluna_obrigatoria_ausente() -> None:
    sem_preco = HEADER.replace(",unit_price", "")
    with pytest.raises(InvalidDatasetError, match="unit_price"):
        CsvDatasetSchema.parse(f"{sem_preco}\n2026-01-05,A,P,1,1,1,0,1\n")


def test_valor_nao_numerico() -> None:
    with pytest.raises(InvalidDatasetError, match="nao e numerica"):
        CsvDatasetSchema.parse(f"{HEADER}\n2026-01-05,A,P,abc,60,240,18.78,0,60\n")


def test_valor_negativo() -> None:
    with pytest.raises(InvalidDatasetError, match="negativo"):
        CsvDatasetSchema.parse(f"{HEADER}\n2026-01-05,A,P,-5,60,240,18.78,0,60\n")


def test_inteiro_fracionario() -> None:
    with pytest.raises(InvalidDatasetError, match="deve ser inteiro"):
        CsvDatasetSchema.parse(f"{HEADER}\n2026-01-05,A,P,10.5,60,240,18.78,0,60\n")


def test_identificador_vazio() -> None:
    with pytest.raises(InvalidDatasetError, match="'sku' vazia"):
        CsvDatasetSchema.parse(f"{HEADER}\n2026-01-05,,P,10,60,240,18.78,0,60\n")


def test_dataset_sem_linhas() -> None:
    with pytest.raises(InvalidDatasetError, match="sem nenhuma linha"):
        CsvDatasetSchema.parse(f"{HEADER}\n")


def test_repositorio_csv_carrega_historico(tmp_path) -> None:  # type: ignore[no-untyped-def]
    arquivo = tmp_path / "dados.csv"
    arquivo.write_text(CSV_VALIDO, encoding="utf-8")
    historico = CsvStockHistoryRepository(arquivo).load_history()
    assert historico.size() == 2


def test_repositorio_csv_arquivo_inexistente(tmp_path) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(InvalidDatasetError, match="nao encontrado"):
        CsvStockHistoryRepository(tmp_path / "ausente.csv").load_history()


def test_catalogo_registra_lista_e_resolve(tmp_path) -> None:  # type: ignore[no-untyped-def]
    catalogo = FilesystemDatasetCatalog(tmp_path)
    resumo = catalogo.register("meu_varejo", CSV_VALIDO)
    assert (resumo.reference, resumo.rows, resumo.skus, resumo.is_builtin) == (
        "meu_varejo",
        2,
        2,
        False,
    )
    referencias = [item.reference for item in catalogo.list_all()]
    assert referencias == ["historico_mensal_v1", "meu_varejo"]
    assert catalogo.path_for("meu_varejo") is not None
    assert catalogo.path_for("inexistente") is None


def test_catalogo_lista_embutido_sem_diretorio(tmp_path) -> None:  # type: ignore[no-untyped-def]
    catalogo = FilesystemDatasetCatalog(tmp_path / "vazio")
    assert [item.reference for item in catalogo.list_all()] == ["historico_mensal_v1"]


def test_catalogo_recusa_sobrescrever_embutido(tmp_path) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(InvalidDatasetError, match="embutido"):
        FilesystemDatasetCatalog(tmp_path).register("historico_mensal_v1", CSV_VALIDO)


@pytest.mark.parametrize("nome", ["", "com espaco", "../fuga", "a" * 65, "-inicio"])
def test_catalogo_recusa_nome_invalido(tmp_path, nome: str) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(InvalidDatasetError):
        FilesystemDatasetCatalog(tmp_path).register(nome, CSV_VALIDO)


def test_catalogo_recusa_csv_invalido_sem_persistir(tmp_path) -> None:  # type: ignore[no-untyped-def]
    catalogo = FilesystemDatasetCatalog(tmp_path)
    with pytest.raises(InvalidDatasetError):
        catalogo.register("quebrado", f"{HEADER}\n2026-01-05,A,P,x,1,1,1,0,1\n")
    assert catalogo.path_for("quebrado") is None
