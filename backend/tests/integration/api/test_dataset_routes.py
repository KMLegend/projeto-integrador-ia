from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from core.config import get_settings
from main import create_application

HEADER = (
    "reference_date,sku,product,stock_on_hand,weekly_outflow,"
    "monthly_outflow,unit_price,promotion_flag,future_demand"
)
CSV_VALIDO = (
    f"{HEADER}\n"
    "2026-01-05,CAFE-500G,Café 500g,192,60,240,18.78,0,60\n"
    "2026-01-05,LEITE-1L,Leite UHT 1L,226,81,324,5.86,1,81\n"
)


@pytest.fixture
def client(tmp_path, monkeypatch) -> Iterator[TestClient]:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("DATASET_STORE_PATH", str(tmp_path / "datasets"))
    get_settings.cache_clear()
    with TestClient(create_application()) as test_client:
        yield test_client
    get_settings.cache_clear()


def _upload(client: TestClient, nome: str, conteudo: str = CSV_VALIDO):  # type: ignore[no-untyped-def]
    return client.post(
        "/api/v1/datasets",
        files={"file": (f"{nome}.csv", conteudo.encode("utf-8"), "text/csv")},
        data={"reference": nome},
    )


def test_lista_inicial_traz_embutido_e_schema(client: TestClient) -> None:
    body = client.get("/api/v1/datasets").json()
    assert [d["reference"] for d in body["datasets"]] == ["historico_mensal_v1"]
    assert body["datasets"][0]["is_builtin"] is True
    assert "unit_price" in body["required_columns"]


def test_upload_registra_e_aparece_na_lista(client: TestClient) -> None:
    resposta = _upload(client, "meu_varejo")
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert (corpo["reference"], corpo["rows"], corpo["skus"]) == ("meu_varejo", 2, 2)

    referencias = [d["reference"] for d in client.get("/api/v1/datasets").json()["datasets"]]
    assert referencias == ["historico_mensal_v1", "meu_varejo"]


def test_upload_usa_nome_do_arquivo_quando_referencia_omitida(client: TestClient) -> None:
    resposta = client.post(
        "/api/v1/datasets",
        files={"file": ("loja_centro.csv", CSV_VALIDO.encode("utf-8"), "text/csv")},
    )
    assert resposta.status_code == 201
    assert resposta.json()["reference"] == "loja_centro"


def test_upload_com_schema_invalido_devolve_422(client: TestClient) -> None:
    quebrado = CSV_VALIDO.replace(",unit_price", ",preco")
    resposta = _upload(client, "ruim", quebrado)
    assert resposta.status_code == 422
    assert resposta.json()["error"]["code"] == "INVALID_DATASET"


def test_upload_nao_sobrescreve_embutido(client: TestClient) -> None:
    resposta = _upload(client, "historico_mensal_v1")
    assert resposta.status_code == 422
    assert resposta.json()["error"]["code"] == "INVALID_DATASET"


def test_otimizacao_aceita_dataset_carregado(client: TestClient) -> None:
    _upload(client, "meu_varejo")
    resposta = client.post(
        "/api/v1/optimize",
        json={
            "budget_limit": 1000.0,
            "dataset_reference": "meu_varejo",
            "ga_parameters": {"population_size": 20, "generations": 5},
        },
    )
    assert resposta.status_code == 202


def test_otimizacao_rejeita_dataset_inexistente(client: TestClient) -> None:
    resposta = client.post(
        "/api/v1/optimize",
        json={
            "budget_limit": 1000.0,
            "dataset_reference": "nunca_enviado",
            "ga_parameters": {"population_size": 20, "generations": 5},
        },
    )
    assert resposta.status_code == 422
    assert resposta.json()["error"]["code"] == "UNKNOWN_DATASET"
