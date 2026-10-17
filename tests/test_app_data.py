"""
Testes da camada de dados do GreenML Dashboard (app/core/data.py).

Os valores esperados são os publicados no artigo (Tabelas 2 a 5 e Figura 4), de modo
que o painel e o texto não possam divergir sem que um teste falhe.
"""

import pytest

from app.core import data


def test_three_datasets_and_seven_contexts_available() -> None:
    assert data.available_datasets() == ["newsgroups", "breast_cancer", "covtype"]
    table = data.contexts_table()
    assert len(table) == 7
    assert table[["lat", "lon"]].notna().all().all()


def test_summary_matches_article_table2_covertype() -> None:
    s = data.model_summary("covtype")
    rl = s.loc["Logistic_Regression"]
    assert list(s.index) == list(data.MODEL_ORDER)
    assert rl.f1_mean == pytest.approx(0.7586, abs=5e-4)
    assert rl.energy_mwh_mean == pytest.approx(1.038, abs=1e-3)
    # Carbono e água recalculados no BR-local (109,95 gCO2e/kWh; 18,58 L/kWh).
    assert rl.carbon_mg == pytest.approx(0.114, abs=1e-3)
    assert rl.water_ul == pytest.approx(19.3, abs=0.1)
    assert (rl.rank_f1, rl.rank_energy, rl.rank_gms) == (4, 1, 1)
    assert int(rl.n_seeds) == 10


def test_gms_ranking_equals_energy_ranking_in_all_datasets() -> None:
    for ds in data.available_datasets():
        s = data.model_summary(ds)
        assert (s.rank_gms == s.rank_energy).all(), ds


def test_relative_score_matches_article_table3() -> None:
    xgb = data.model_summary("covtype").loc["XGBoost"]
    assert xgb.energy_ratio_ref == pytest.approx(5.14, abs=0.01)
    assert xgb.delta_f1_points == pytest.approx(10.36, abs=0.01)
    assert xgb.marginal_cost_j == pytest.approx(1.64, abs=0.01)
    assert xgb.dominated_share == 0
    mlp = data.model_summary("newsgroups").loc["MLP_Neural_Network"]
    assert mlp.marginal_cost_j == pytest.approx(87.30, abs=0.01)
    assert mlp.dominated_share == pytest.approx(0.7)


def test_decision_table_matches_article_table4() -> None:
    d = data.decision_table("covtype")
    chosen = dict(zip(d.criterio, d.modelo))
    assert chosen["Maior F1-Score"] == "Random_Forest"
    assert chosen["Menor energia"] == "Logistic_Regression"
    assert chosen["Maior GMS"] == "Logistic_Regression"
    front = set(d[d.criterio == "Fronteira de Pareto"].modelo)
    assert front == {"Logistic_Regression", "XGBoost", "Random_Forest"}
    rf = d[d.criterio == "Maior F1-Score"].iloc[0]
    assert rf.carbono_mg == pytest.approx(4.02, abs=0.01)
    single = data.decision_table("newsgroups")
    assert set(single.modelo) == {"Logistic_Regression"}


def test_profiles_match_article_table5() -> None:
    p = data.profile_summary("covtype").set_index("perfil")
    assert p.loc["Pesos iguais", "tau_b"] == pytest.approx(0.882, abs=1e-3)
    assert p.loc["Pesos iguais", "pares_invertidos"] == 0
    assert p.loc["Só carbono", "tau_b"] == pytest.approx(0.696, abs=1e-3)
    assert p.loc["Só carbono", "melhor_contexto"] == "AWS-Stockholm"
    assert p.loc["Só carbono", "pior_contexto"] == "IN-local"
    assert p.loc["Só água", "melhor_contexto"] == "AWS-Frankfurt"
    ng = data.profile_summary("newsgroups").set_index("perfil")
    assert ng.loc["Pesos iguais", "pares_invertidos"] == 14
    assert ng.loc["Só energia", "tau_b"] == pytest.approx(1.0)


def test_carbon_only_inversion_of_figure4() -> None:
    ev = data.evaluate_context("covtype", data.make_weights(0, 1, 0))
    cfg = ev.configurations.set_index(["model", "context"]).gms
    assert cfg["XGBoost", "AWS-Stockholm"] == pytest.approx(99.6, abs=0.05)
    assert cfg["Logistic_Regression", "IN-local"] == pytest.approx(98.8, abs=0.05)
    inv = data.inversions(ev.configurations)
    pair = inv[
        (inv.vencedor == "XGBoost")
        & (inv.contexto_vencedor == "AWS-Stockholm")
        & (inv.superado == "Logistic_Regression")
        & (inv.contexto_superado == "IN-local")
    ]
    assert len(pair) == 1


def test_k_factor_reproduces_gms() -> None:
    w = data.make_weights(1, 1, 1)
    contexts = data.load_contexts()
    ev = data.evaluate_context("newsgroups", w, contexts)
    k = data.k_factors(ev.configurations, contexts, w)
    for _, row in ev.configurations.iterrows():
        assert row.gms == pytest.approx(
            100 * (1 - row.energy_kwh * k[row.context]), abs=1e-6
        )


def test_make_weights_normalizes_and_rejects_invalid() -> None:
    w = data.make_weights(2, 1, 1)
    assert (w.w_E, w.w_C, w.w_W) == pytest.approx((0.5, 0.25, 0.25))
    with pytest.raises(ValueError):
        data.make_weights(0, 0, 0)
    with pytest.raises(ValueError):
        data.make_weights(-1, 1, 1)


def test_missing_dataset_raises() -> None:
    with pytest.raises(FileNotFoundError):
        data.load_runs("inexistente")


def test_labels_match_experiments_labels() -> None:
    from experiments import labels

    assert data.DATASET_NAMES == labels.DATASET_NAMES
    assert data.MODEL_NAMES == labels.MODEL_NAMES
