"""
Testes de fumaça das páginas do GreenML Dashboard: cada página roda, sem exceções,
para cada conjunto de dados (streamlit.testing.v1.AppTest, sem navegador).
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

DATASETS = ["newsgroups", "breast_cancer", "covtype"]
PAGES = ["app/views/1_visao_geral.py", "app/views/2_qualidade_custo.py"]


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
