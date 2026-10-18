"""
theme.py: cores e formatação do GreenML Dashboard.

As cores dos modelos são as mesmas das figuras do artigo; a paleta principal usa o
verde do GMS com contraste alto, pensando em projeção.
"""

from __future__ import annotations

import math

GREEN = "#1B7F3B"
GREEN_DARK = "#0E4D23"
GREEN_LIGHT = "#EEF6F0"
GREY = "#5F6B66"

MODEL_COLORS: dict[str, str] = {
    "Logistic_Regression": "#2CA02C",
    "Random_Forest": "#1F77B4",
    "XGBoost": "#D62728",
    "MLP_Neural_Network": "#FF7F0E",
}
# Escala sequencial para o GMS (0 = pior, 100 = melhor).
GMS_SCALE: list[list[float | str]] = [
    [0.0, "#F7FCF5"],
    [0.5, "#74C476"],
    [1.0, "#00441B"],
]


def fmt(value: float, decimals: int = 2, unit: str = "") -> str:
    """Número com vírgula decimal e separador de milhar com ponto."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "n.a."
    text = (
        f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    text = text.replace("-", "−")
    return f"{text} {unit}".strip()


def fmt_auto(value: float, unit: str = "") -> str:
    """Número com casas decimais conforme a ordem de grandeza."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "n.a."
    a = abs(value)
    decimals = 3 if a < 1 else 2 if a < 10 else 1 if a < 1000 else 0
    return fmt(value, decimals, unit)


def fmt_pct(value: float, decimals: int = 0) -> str:
    """Fração (0 a 1) como porcentagem."""
    return fmt(100 * value, decimals) + "%"


def br_table(df, columns: dict[str, tuple[str, int | str]]):
    """
    Cópia da tabela só com as colunas pedidas, renomeadas e formatadas como texto com
    vírgula decimal. ``columns`` mapeia coluna -> (rótulo, casas decimais); use
    ``"+1"`` para forçar o sinal com uma casa e ``"pct"`` para porcentagem.
    """
    out = df[list(columns)].copy()
    for col, (_, spec) in columns.items():
        if spec == "pct":
            out[col] = [fmt_pct(v) for v in out[col]]
        elif isinstance(spec, str) and spec.startswith("+"):
            d = int(spec[1:])
            out[col] = [("+" if v > 0 else "") + fmt(v, d) for v in out[col]]
        elif isinstance(spec, int):
            out[col] = [fmt(v, spec) for v in out[col]]
    return out.rename(columns={c: label for c, (label, _) in columns.items()})


def kpi_html(label: str, value: str, sub: str | None = None) -> str:
    """Cartão de indicador em HTML (sem setas de variação e sem truncar o valor)."""
    sub_html = (
        f"<div style='font-size:0.9rem;color:{GREY};margin-top:2px'>{sub}</div>"
        if sub
        else ""
    )
    return (
        f"<div style='border:1px solid #DDE6DF;border-radius:10px;padding:10px 14px;"
        f"background:{GREEN_LIGHT};height:100%'>"
        f"<div style='font-size:0.9rem;color:{GREY}'>{label}</div>"
        f"<div style='font-size:1.55rem;font-weight:700;line-height:1.25'>{value}</div>"
        f"{sub_html}</div>"
    )
