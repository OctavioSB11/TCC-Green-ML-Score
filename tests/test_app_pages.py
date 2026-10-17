"""
Testes de fumaça das páginas do GreenML Dashboard: cada página roda, sem exceções,
para cada conjunto de dados (streamlit.testing.v1.AppTest, sem navegador).
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

DATASETS = ["newsgroups", "breast_cancer", "covtype"]
PAGES = [
    "app/views/1_visao_geral.py",
    "app/views/2_qualidade_custo.py",
    "app/views/3_simulador.py",
    "app/views/4_cartao.py",
    "app/views/5_avalie.py",
]


def _run(page: str, dataset: str) -> AppTest:
    at = AppTest.from_file(str(ROOT / page), default_timeout=120)
    at.session_state["dataset"] = dataset
    at.run()
    return at


@pytest.mark.parametrize("dataset", DATASETS)
@pytest.mark.parametrize("page", PAGES)
def test_page_runs_without_exceptions(page: str, dataset: str) -> None:
    at = _run(page, dataset)
    assert not at.exception
    assert at.title


def test_quality_cost_compares_against_lowest_marginal_cost() -> None:
    at = _run("app/views/2_qualidade_custo.py", "covtype")
    message = at.info[0].value
    assert message.startswith("Trocar Regressão Logística por XGBoost")
    assert "1,64 J por ponto" in message


def test_simulator_carbon_only_shows_xgboost_overtaking_rl() -> None:
    at = AppTest.from_file(str(ROOT / "app/views/3_simulador.py"), default_timeout=120)
    at.session_state["dataset"] = "covtype"
    at.run()
    at.session_state["sim_we"] = 0
    at.session_state["sim_wc"] = 100
    at.session_state["sim_ww"] = 0
    at.run()
    assert not at.exception
    warning = at.warning[0].value
    assert "XGBoost em AWS-Stockholm (99,6)" in warning
    assert "Regressão Logística em IN-local (98,8)" in warning


def test_simulator_equal_weights_has_no_model_change() -> None:
    at = _run("app/views/3_simulador.py", "covtype")
    assert not at.exception
    assert not at.warning
    assert at.success  # nenhuma inversão no Covertype com pesos iguais


def test_evaluate_page_example_shows_results_and_download() -> None:
    at = _run("app/views/5_avalie.py", "covtype")
    assert not at.exception
    assert not at.error
    assert at.selectbox(key="av_regiao").value == "BR-local"
    # Exemplo do Covertype: XGBoost com o menor custo marginal frente à RL.
    assert any(
        "XGBoost: 1,64 J por ponto de F1" in s.value for s in at.success
    ), at.success
    assert len(at.dataframe) == 1
    assert at.toggle(key="av_estudo").disabled


def test_evaluate_page_breast_cancer_example_has_rl_dominating() -> None:
    at = _run("app/views/5_avalie.py", "breast_cancer")
    assert not at.exception
    assert any("Nenhum modelo supera" in w.value for w in at.warning)


def test_evaluate_page_waits_for_upload_without_errors() -> None:
    at = AppTest.from_file(str(ROOT / "app/views/5_avalie.py"), default_timeout=120)
    at.session_state["dataset"] = "covtype"
    at.session_state["av_fonte"] = "Enviar meu CSV"
    at.run()
    assert not at.exception
    assert not at.error
    assert any("Envie um arquivo" in c.value for c in at.caption)
