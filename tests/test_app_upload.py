"""Testes da avaliação de resultados enviados pelo usuário (app/core/upload.py)."""

import pandas as pd
import pytest

from app.core import charts, data, upload


def _csv(text: str) -> bytes:
    return text.encode("utf-8")


# ------------------------------------------------------------------ leitura
def test_example_csv_round_trip_matches_study_runs() -> None:
    loaded = upload.read_upload(upload.example_csv())
    runs = data.load_runs(upload.EXAMPLE_DATASET)
    assert loaded.unit == "kWh"
    assert len(loaded.runs) == len(runs) == 40
    assert set(loaded.models) == set(data.MODEL_ORDER)
    got = loaded.runs.groupby("model").energy_kwh.median()
    expected = runs.groupby("model_name").energy_kwh.median()
    pd.testing.assert_series_equal(
        got.sort_index(), expected.sort_index(), check_names=False, rtol=1e-9
    )


def test_semicolon_decimal_comma_and_units() -> None:
    raw = _csv("Modelo;F1-Score;Energia\nA;0,85;3,6\nA;0,87;7,2\nB;0,9;36\n")
    in_j = upload.read_upload(raw, unit="J")
    assert in_j.runs.energy_kwh.tolist() == pytest.approx([1e-6, 2e-6, 1e-5])
    assert in_j.runs.seed.tolist() == [1, 2, 1]
    in_wh = upload.read_upload(raw, unit="Wh")
    assert in_wh.runs.energy_kwh.iloc[0] == pytest.approx(3.6e-3)


def test_comma_separator_and_unit_from_column_name() -> None:
    raw = _csv("model,seed,f1_macro,energy (J)\nA,1,0.8,3600\nB,1,0.9,7200\n")
    loaded = upload.read_upload(raw, unit="kWh")
    assert loaded.unit == "J"
    assert loaded.runs.energy_kwh.tolist() == pytest.approx([1e-3, 2e-3])


def test_blank_lines_are_dropped_with_a_note() -> None:
    raw = _csv("modelo;f1;energia\nA;0,8;1\n;;\nB;0,9;2\n")
    loaded = upload.read_upload(raw)
    assert len(loaded.runs) == 2
    assert loaded.notes and "vazia" in loaded.notes[0]


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        (b"", "vazio"),
        (b"modelo;f1\nA;0,9\n", "Faltam colunas obrigatórias: energia"),
        (b"modelo;f1;energia\nA;85;1\n", "divida por 100"),
        (
            b"modelo;f1;energia\nA;0,9;-1\nB;0,8;-2\n",
            "energia negativa nas linhas 2, 3",
        ),
        (b"modelo;f1;energia\nA;0,9;0\n", "energia igual a zero na linha 2"),
        (b"modelo;f1;energia\nA;0,9;abc\n", "valor de energia vazio ou não numérico"),
        (b"modelo;f1;energia\n;0,9;1\n", "modelo em branco na linha 2"),
        (b"modelo;f1;energia\n;;\n", "nenhuma linha de dados"),
    ],
)
def test_invalid_files_raise_clear_messages(raw: bytes, message: str) -> None:
    with pytest.raises(upload.UploadError, match=message):
        upload.read_upload(raw)


def test_unknown_unit_is_rejected() -> None:
    with pytest.raises(upload.UploadError):
        upload.read_upload(b"modelo;f1;energia\nA;0,9;1\n", unit="cal")


# ------------------------------------------------------------------ cálculo
def test_example_reproduces_simulator_and_card_numbers() -> None:
    runs = upload.read_upload(upload.example_csv("covtype")).runs
    assert upload.default_reference(runs) == data.REFERENCE_MODEL
    w = data.make_weights(0, 1, 0)
    ev = upload.evaluate(runs, data.REFERENCE_MODEL, "AWS-Stockholm", w)
    xgb = ev.summary.loc["XGBoost"]
    # Mesmos números do cartão ambiental e da Figura 4 do artigo.
    assert round(xgb.gms, 1) == 99.6
    assert xgb.rank_context == 5
    assert round(xgb.carbon_mg, 3) == 0.223
    assert round(xgb.water_ul, 1) == 38.1
    assert round(xgb.marginal_cost_j, 2) == 1.64
    sim = data.simulate("covtype", w)
    merged = ev.configurations.merge(
        sim["configurations"], on=["model", "context"], suffixes=("", "_sim")
    )
    assert len(merged) == 28
    assert merged.gms.to_numpy() == pytest.approx(merged.gms_sim.to_numpy())
    assert len(ev.inversions) == len(sim["inversions"]) == 31
    assert list(ev.k.index) == list(sim["k"].index)


def test_pareto_and_d4_reading_follow_the_article() -> None:
    runs = upload.read_upload(upload.example_csv("covtype")).runs
    s = upload.evaluate(runs, data.REFERENCE_MODEL).summary
    study = data.model_summary("covtype")
    assert s.pareto.to_dict() == study.pareto.to_dict()
    # Covertype: H2 refutada pelo XGBoost (na fronteira com cerca de 5 vezes E_ref).
    assert s.h2["XGBoost"] == "Contraria H2"
    assert s.h2["MLP_Neural_Network"] == "Compatível (dominado)"
    assert s.h2["Random_Forest"] == "Compatível (E/E_ref ≥ 10)"
    assert s.h2[data.REFERENCE_MODEL] == "Referência"


@pytest.mark.parametrize(
    ("is_ref", "pareto", "ratio", "expected"),
    [
        (True, True, 1.0, "Referência"),
        (False, False, 2.0, "Compatível (dominado)"),
        (False, True, 10.0, "Compatível (E/E_ref ≥ 10)"),
        (False, True, 9.99, "Contraria H2"),
    ],
)
def test_h2_reading(is_ref: bool, pareto: bool, ratio: float, expected: str) -> None:
    assert upload.h2_reading(is_ref, pareto, ratio) == expected


def test_user_models_with_custom_reference_and_result_csv() -> None:
    raw = _csv("modelo;f1;energia\nA;0,85;3\nA;0,86;4\nB;0,90;30\nC;0,80;40\n")
    runs = upload.read_upload(raw, unit="J").runs
    assert upload.default_reference(runs) == "A"
    ev = upload.evaluate(runs, "A")
    s = ev.summary
    assert len(ev.configurations) == 3 * 7
    assert s.delta_f1_points["B"] == pytest.approx(4.5)
    assert s.marginal_cost_j["B"] == pytest.approx((30 - 3.5) / 4.5)
    assert pd.isna(s.marginal_cost_j["C"])
    assert not s.pareto["C"] and s.h2["C"] == "Compatível (dominado)"
    assert s.h2["B"] == "Contraria H2"
    text = upload.result_csv(ev, data.make_weights(1, 1, 1)).decode("utf-8-sig")
    header = text.splitlines()[0].split(";")
    assert header[0] == "modelo" and "regra_d4_h2" in header
    assert "Contraria H2" in text and "—" not in text
    with pytest.raises(KeyError):
        upload.evaluate(runs, "Z")
    with pytest.raises(KeyError):
        upload.evaluate(runs, "A", "Lua")


def test_charts_accept_user_models() -> None:
    raw = _csv("modelo;f1;energia\nA;0,85;3\nB;0,90;30\n")
    loaded = upload.read_upload(raw, unit="J")
    ev = upload.evaluate(loaded.runs, "A")
    fig = charts.pareto_chart(
        ev.summary,
        upload.seed_points(loaded.runs),
        reference="A",
        reference_short="ref",
    )
    names = [t.name for t in fig.data]
    assert "A (referência)" in names and "B" in names
    b = next(t for t in fig.data if t.name == "B")
    assert "E/E_ref" in b.hovertemplate
    charts.add_study_points(fig, data.model_summary("covtype"), "covtype")
    assert fig.data[-1].name == "Modelos do estudo (Covertype)"
    heat = charts.gms_heatmap(ev.configurations, list(ev.k.index))
    assert list(heat.data[0].y) == ["A", "B"]
