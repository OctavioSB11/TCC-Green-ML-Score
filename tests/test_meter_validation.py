"""
test_meter_validation.py — Análise da validação do CodeCarbon com medidor de tomada.
"""

import math

import pandas as pd
import pytest

from experiments.meter_validation import analyze, build_report


def _df(**overrides) -> pd.DataFrame:
    rows = [
        # 600 s a 30 W (medidor) e 20 W (CodeCarbon) em repouso
        {
            "trial": 1,
            "phase": "idle",
            "duration_s": 600.0,
            "cc_energy_wh": 20 / 6,
            "meter_energy_wh": 5.0,
        },
        # carga: +15 W no medidor, +12 W no CodeCarbon
        {
            "trial": 1,
            "phase": "load",
            "duration_s": 600.0,
            "cc_energy_wh": 32 / 6,
            "meter_energy_wh": 7.5,
        },
    ]
    df = pd.DataFrame(rows)
    for k, v in overrides.items():
        df[k] = v
    return df


def test_analyze_power_and_incremental_energy() -> None:
    r = analyze(_df()).iloc[0]
    assert r["meter_idle_w"] == pytest.approx(30.0)
    assert r["cc_idle_w"] == pytest.approx(20.0)
    assert r["meter_load_w"] == pytest.approx(45.0)
    assert r["meter_delta_wh"] == pytest.approx(2.5)
    assert r["cc_delta_wh"] == pytest.approx(2.0)
    assert r["ratio_delta"] == pytest.approx(0.8)
    assert r["ratio_load"] == pytest.approx((32 / 6) / 7.5)


def test_analyze_scales_idle_to_load_duration() -> None:
    df = _df()
    df.loc[0, ["duration_s", "meter_energy_wh", "cc_energy_wh"]] = [300.0, 2.5, 10 / 6]
    r = analyze(df).iloc[0]
    assert r["meter_delta_wh"] == pytest.approx(2.5)
    assert r["cc_delta_wh"] == pytest.approx(2.0)


def test_analyze_rejects_missing_reading_or_phase() -> None:
    df = _df()
    df.loc[1, "meter_energy_wh"] = None
    with pytest.raises(ValueError, match="ausentes"):
        analyze(df)
    with pytest.raises(ValueError, match="idle e load"):
        analyze(_df().iloc[:1])


def test_nonpositive_meter_delta_gives_nan_ratio() -> None:
    df = _df()
    df.loc[1, "meter_energy_wh"] = 5.0
    assert math.isnan(analyze(df).iloc[0]["ratio_delta"])


def test_report_renders(tmp_path) -> None:
    per_trial = analyze(pd.concat([_df(), _df(trial=2)]))
    md = build_report(per_trial, tmp_path / "x.csv")
    assert "tentativas: 2" in md
    assert "Energia incremental" in md
