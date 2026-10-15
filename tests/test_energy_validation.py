"""
test_energy_validation.py — Validação física (bateria ou medidor) das estimativas
do CodeCarbon.
"""

import math

import numpy as np
import pandas as pd
import pytest

from experiments.energy_validation import (
    BatterySampler,
    ValidationError,
    analyze,
    build_report,
    integrate_power_wh,
)


def _df(**overrides) -> pd.DataFrame:
    rows = [
        # 600 s a 30 W (referência) e 20 W (CodeCarbon) em repouso
        {
            "trial": 1,
            "phase": "idle",
            "duration_s": 600.0,
            "cc_energy_wh": 20 / 6,
            "ref_energy_wh": 5.0,
        },
        # carga: +15 W na referência, +12 W no CodeCarbon
        {
            "trial": 1,
            "phase": "load",
            "duration_s": 600.0,
            "cc_energy_wh": 32 / 6,
            "ref_energy_wh": 7.5,
        },
    ]
    df = pd.DataFrame(rows)
    for k, v in overrides.items():
        df[k] = v
    return df


# ---------------------------------------------------------------------------
# Integração da potência
# ---------------------------------------------------------------------------


def test_integrate_constant_power() -> None:
    t = np.arange(0, 101, 1.0)
    assert integrate_power_wh(t, np.full_like(t, 36.0), 10.0, 110.0) == pytest.approx(
        1.0
    )  # 36 W × 100 s = 1 Wh (último valor vale até t1)


def test_integrate_piecewise_uses_value_in_force_at_t0() -> None:
    # 10 W até t = 50, depois 46 W; janela [20, 80] → 30 s × 10 W + 30 s × 46 W
    t = np.array([0.0, 50.0])
    p = np.array([10.0, 46.0])
    expected = (30 * 10 + 30 * 46) / 3600
    assert integrate_power_wh(t, p, 20.0, 80.0) == pytest.approx(expected)


def test_integrate_rejects_invalid_window() -> None:
    with pytest.raises(ValueError):
        integrate_power_wh(np.array([5.0]), np.array([1.0]), 0.0, 10.0)
    with pytest.raises(ValueError):
        integrate_power_wh(np.array([0.0]), np.array([1.0]), 10.0, 10.0)


def test_sampler_phase_energy_and_charger_detection() -> None:
    s = BatterySampler(
        times_s=[0.0, 10.0, 20.0, 30.0],
        capacity_mwh=[30000.0, 30000.0, 29410.0, 29410.0],
        rate_mw=[18000.0, 18000.0, 18000.0, 18000.0],
        online=[False, False, False, False],
    )
    rate_wh, cap_wh = s.phase_energy(5.0, 25.0)
    assert rate_wh == pytest.approx(18 * 20 / 3600)
    assert cap_wh == pytest.approx(0.59)
    s.online[2] = True
    with pytest.raises(ValidationError, match="Carregador"):
        s.phase_energy(5.0, 25.0)
    with pytest.raises(ValidationError, match="Carregador"):
        BatterySampler(online=[True], capacity_mwh=[1.0]).check_on_battery(0.0)
    with pytest.raises(ValidationError, match="abaixo"):
        BatterySampler(online=[False], capacity_mwh=[100.0]).check_on_battery(500.0)


# ---------------------------------------------------------------------------
# Análise
# ---------------------------------------------------------------------------


def test_analyze_power_and_incremental_energy() -> None:
    r = analyze(_df()).iloc[0]
    assert r["ref_idle_w"] == pytest.approx(30.0)
    assert r["cc_idle_w"] == pytest.approx(20.0)
    assert r["ref_load_w"] == pytest.approx(45.0)
    assert r["ref_delta_wh"] == pytest.approx(2.5)
    assert r["cc_delta_wh"] == pytest.approx(2.0)
    assert r["ratio_delta"] == pytest.approx(0.8)
    assert r["ratio_load"] == pytest.approx((32 / 6) / 7.5)


def test_analyze_scales_idle_to_load_duration() -> None:
    df = _df()
    df.loc[0, ["duration_s", "ref_energy_wh", "cc_energy_wh"]] = [300.0, 2.5, 10 / 6]
    r = analyze(df).iloc[0]
    assert r["ref_delta_wh"] == pytest.approx(2.5)
    assert r["cc_delta_wh"] == pytest.approx(2.0)


def test_analyze_rejects_missing_reading_or_phase() -> None:
    df = _df()
    df.loc[1, "ref_energy_wh"] = None
    with pytest.raises(ValueError, match="ausentes"):
        analyze(df)
    with pytest.raises(ValueError, match="idle e load"):
        analyze(_df().iloc[:1])


def test_nonpositive_reference_delta_gives_nan_ratio() -> None:
    df = _df()
    df.loc[1, "ref_energy_wh"] = 5.0
    assert math.isnan(analyze(df).iloc[0]["ratio_delta"])


def test_report_renders(tmp_path) -> None:
    per_trial = analyze(pd.concat([_df(), _df(trial=2)]))
    md = build_report(per_trial, tmp_path / "x.csv", "battery")
    assert "tentativas: 2" in md
    assert "referência: **battery**" in md
    assert "Energia incremental" in md
