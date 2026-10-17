"""Testes do cartão ambiental do painel (app/core/card.py)."""

import pytest

from app.core import card


def test_card_matches_article_for_xgboost_in_stockholm() -> None:
    c = card.build_card("covtype", "XGBoost", "AWS-Stockholm", "Só carbono")
    # Valores do artigo: 0,22 mg de CO2e e 38 µL de água por treinamento.
    assert c.carbon_mg == pytest.approx(0.223, abs=1e-3)
    assert c.water_ul == pytest.approx(38.1, abs=0.1)
    assert round(c.gms_context, 1) == 99.6
    assert c.marginal_cost_j == pytest.approx(1.64, abs=0.01)
    assert c.pareto and not c.is_reference
    assert c.n_seeds == 10
    assert c.trainings_per_charge == pytest.approx(0.019 / 5.7927e-6, rel=1e-3)


def test_reference_card_has_no_relative_values() -> None:
    c = card.build_card("newsgroups", "Logistic_Regression", "BR-local")
    assert c.is_reference
    assert c.energy_ratio_ref is None and c.marginal_cost_j is None
    assert "execução local: PUE 1 e WUE 0" in card.short_sources(c)


def test_exports_markdown_csv_png() -> None:
    c = card.build_card("covtype", "Random_Forest", "FR-local", "Pesos iguais")
    md = card.to_markdown(c)
    assert md.startswith("# Cartão ambiental: Random Forest em FR-local")
    assert "9,32 J por ponto de F1" in md
    assert "—" not in md
    csv = card.to_csv(c).decode("utf-8-sig")
    assert csv.splitlines()[0] == "Seção;Indicador;Valor"
    png = card.to_png(c)
    assert png[:8] == b"\x89PNG\r\n\x1a\n" and len(png) > 20_000


def test_annual_projection_scales_linearly() -> None:
    c = card.build_card("covtype", "XGBoost", "BR-local")
    one = card.annual_projection(c, 1)
    ten = card.annual_projection(c, 10)
    assert ten["energia_kwh"] == pytest.approx(10 * one["energia_kwh"])
    assert one["energia_kwh"] == pytest.approx(365 * c.energy_mwh_median / 1e6)


def test_unknown_model_raises() -> None:
    with pytest.raises(KeyError):
        card.build_card("covtype", "SVM", "BR-local")
