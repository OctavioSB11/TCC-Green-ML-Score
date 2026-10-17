"""
upload.py: avaliação de resultados enviados pelo usuário (tarefa T6).

Lê um CSV com uma linha por treinamento (modelo, F1-Score, energia e, se houver,
semente), valida o conteúdo com mensagens em português e calcula, com as mesmas
funções do restante do painel e da biblioteca, o GMS em cada região, a fronteira de
Pareto, o custo frente a um modelo de referência e a leitura da regra D4 de H2.
Não depende do Streamlit.
"""

from __future__ import annotations

import io
import math
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from app.core import data
from green_ml_score.contexts import ExecutionContext, evaluate_configurations
from green_ml_score.scoring.gms import Weights
from green_ml_score.scoring.relative import pareto_dominated, relative_to_reference

# Unidades de energia aceitas e o fator para converter em kWh.
UNITS: dict[str, float] = {"kWh": 1.0, "Wh": 1e-3, "J": 1.0 / data.KWH_TO_J}
# Limiar da regra D4: um modelo na fronteira só é compatível com H2 se E/E_ref ≥ 10.
H2_THRESHOLD = 10.0
MAX_ROWS = 20_000
MAX_MODELS = 20
EXAMPLE_DATASET = "breast_cancer"

# Nomes aceitos para cada coluna (comparados sem acento e sem diferenciar maiúsculas).
ALIASES: dict[str, tuple[str, ...]] = {
    "model": ("modelo", "model", "model_name", "nome"),
    "f1": ("f1", "f1_score", "f1_macro", "f1score"),
    "energy": (
        "energia",
        "energy",
        "energia_kwh",
        "energy_kwh",
        "energia_j",
        "energy_j",
    ),
    "seed": ("semente", "seed", "repeticao", "execucao"),
}
# Colunas cujo nome já traz a unidade, que prevalece sobre a escolha da tela.
UNIT_FROM_NAME: dict[str, str] = {
    "energia_kwh": "kWh",
    "energy_kwh": "kWh",
    "energia_j": "J",
    "energy_j": "J",
}


class UploadError(ValueError):
    """Erro de formato ou de conteúdo do CSV enviado, com mensagem para o usuário."""


@dataclass
class UploadedRuns:
    """
    Treinamentos lidos do CSV, já validados.

    Atributos:
        runs     : uma linha por treinamento, com ``model``, ``seed``, ``f1`` e
                   ``energy_kwh``.
        unit     : unidade de energia usada na leitura.
        notes    : avisos que não impedem o cálculo (linhas vazias descartadas etc.).
    """

    runs: pd.DataFrame
    unit: str
    notes: list[str] = field(default_factory=list)

    @property
    def models(self) -> list[str]:
        return list(dict.fromkeys(self.runs.model))


def _plain(text: str) -> str:
    """Nome de coluna sem acentos, espaços nas pontas e maiúsculas."""
    norm = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    key = norm.strip().lower()
    for char in " -()[]":
        key = key.replace(char, "_")
    return "_".join(part for part in key.split("_") if part)


def _decode(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise UploadError("Não foi possível ler o arquivo como texto (use UTF-8).")


def _lines(index: Sequence[int]) -> str:
    """Linhas do arquivo (o cabeçalho é a linha 1), no máximo dez, com a preposição."""
    shown = [str(i + 2) for i in list(index)[:10]]
    more = len(index) - len(shown)
    prefix = "na linha" if len(index) == 1 else "nas linhas"
    return f"{prefix} " + ", ".join(shown) + (f" e mais {more}" if more > 0 else "")


def _to_number(column: pd.Series) -> pd.Series:
    """Converte texto em número aceitando vírgula decimal (1,5 ou 1.234,5)."""
    text = column.astype(str).str.strip()
    comma = text.str.contains(",", regex=False)
    text = text.where(~comma, text.str.replace(".", "", regex=False))
    text = text.str.replace(",", ".", regex=False)
    return pd.to_numeric(text.replace({"": np.nan, "nan": np.nan}), errors="coerce")


def read_upload(raw: bytes, unit: str = "kWh") -> UploadedRuns:
    """
    Lê e valida o CSV enviado.

    Aceita separador ``;`` ou ``,`` e vírgula ou ponto decimal. Colunas mínimas:
    modelo, f1 (entre 0 e 1) e energia (positiva, na unidade ``unit``, salvo se o
    nome da coluna já indicar a unidade); a semente é opcional.

    Raises:
        UploadError: arquivo vazio, colunas faltando ou valores inválidos.
    """
    if unit not in UNITS:
        raise UploadError(f"Unidade de energia desconhecida: {unit}.")
    text = _decode(raw).strip()
    if not text:
        raise UploadError("O arquivo está vazio.")
    header = text.splitlines()[0]
    sep = ";" if header.count(";") >= header.count(",") and ";" in header else ","
    try:
        df = pd.read_csv(io.StringIO(text), sep=sep, dtype=str, skip_blank_lines=False)
    except pd.errors.ParserError as exc:
        raise UploadError(
            "Não foi possível separar as colunas: confira se todas as linhas têm o "
            f"mesmo número de campos ({exc})."
        ) from exc

    found: dict[str, str] = {}
    for col in df.columns:
        key = _plain(col)
        for target, names in ALIASES.items():
            if key in names and target not in found:
                found[target] = col
    missing = [name for name in ("model", "f1", "energy") if name not in found]
    if missing:
        label = {"model": "modelo", "f1": "f1", "energy": "energia"}
        raise UploadError(
            "Faltam colunas obrigatórias: "
            + ", ".join(label[m] for m in missing)
            + ". O arquivo precisa ter pelo menos modelo, f1 e energia; colunas "
            f"encontradas: {', '.join(map(str, df.columns))}."
        )

    notes: list[str] = []
    unit = UNIT_FROM_NAME.get(_plain(found["energy"]), unit)
    out = pd.DataFrame(
        {
            "model": df[found["model"]].astype(str).str.strip(),
            "f1": _to_number(df[found["f1"]]),
            "energy": _to_number(df[found["energy"]]),
        }
    )
    out.loc[df[found["model"]].isna(), "model"] = ""
    out["seed"] = (
        _to_number(df[found["seed"]])
        if "seed" in found
        else pd.Series(np.nan, df.index)
    )

    blank = (out.model == "") & out.f1.isna() & out.energy.isna()
    if blank.any():
        notes.append(f"{int(blank.sum())} linha(s) vazia(s) descartada(s).")
    out = out[~blank]
    if out.empty:
        raise UploadError("O arquivo não tem nenhuma linha de dados.")
    if len(out) > MAX_ROWS:
        raise UploadError(f"O arquivo tem {len(out)} linhas; o limite é {MAX_ROWS}.")

    problems: list[str] = []
    no_model = out.index[out.model == ""]
    if len(no_model):
        problems.append(f"modelo em branco {_lines(no_model)}")
    for col, name in (("f1", "f1"), ("energy", "energia")):
        bad = out.index[out[col].isna()]
        if len(bad):
            problems.append(f"valor de {name} vazio ou não numérico {_lines(bad)}")
    bad_f1 = out.index[out.f1.notna() & ((out.f1 < 0) | (out.f1 > 1))]
    if len(bad_f1):
        hint = " (parece estar em %: divida por 100)" if out.f1.max() <= 100 else ""
        problems.append(f"f1 fora do intervalo de 0 a 1{hint} {_lines(bad_f1)}")
    negative = out.index[out.energy.notna() & (out.energy < 0)]
    if len(negative):
        problems.append(f"energia negativa {_lines(negative)}")
    zero = out.index[out.energy == 0]
    if len(zero):
        problems.append(f"energia igual a zero {_lines(zero)}")
    if problems:
        raise UploadError("Valores inválidos: " + "; ".join(problems) + ".")

    n_models = out.model.nunique()
    if n_models > MAX_MODELS:
        raise UploadError(f"O arquivo tem {n_models} modelos; o limite é {MAX_MODELS}.")
    if out.seed.isna().any():
        if out.seed.notna().any():
            notes.append(
                "Algumas linhas sem semente foram numeradas pela ordem no arquivo."
            )
        order = out.groupby("model").cumcount() + 1
        out["seed"] = out.seed.fillna(order.astype(float))
    out["energy_kwh"] = out.energy * UNITS[unit]
    runs = out[["model", "seed", "f1", "energy_kwh"]].reset_index(drop=True)
    runs["seed"] = runs.seed.astype(int)
    return UploadedRuns(runs=runs, unit=unit, notes=notes)


# ------------------------------------------------------------------ exemplo
def example_runs(dataset: str = EXAMPLE_DATASET) -> pd.DataFrame:
    """Treinamentos de um dataset do estudo no formato de envio (energia em kWh)."""
    df = data.load_runs(dataset)
    return pd.DataFrame(
        {
            "modelo": df.model_name,
            "semente": df.seed,
            "f1": df.f1_macro,
            "energia_kwh": df.energy_kwh,
        }
    ).reset_index(drop=True)


def example_csv(dataset: str = EXAMPLE_DATASET) -> bytes:
    """CSV de exemplo (separador ``;`` e vírgula decimal, abre direto no Excel)."""
    return (
        example_runs(dataset)
        .to_csv(sep=";", decimal=",", index=False, float_format="%.10g")
        .encode("utf-8-sig")
    )


# ------------------------------------------------------------------ cálculo
def default_reference(runs: pd.DataFrame) -> str:
    """Modelo de menor energia mediana, referência padrão."""
    return str(runs.groupby("model").energy_kwh.median().idxmin())


def h2_reading(is_reference: bool, pareto: bool, ratio: float) -> str:
    """Leitura da regra D4: dominado ou na fronteira com E/E_ref ≥ 10 é compatível."""
    if is_reference:
        return "Referência"
    if not pareto:
        return "Compatível (dominado)"
    if ratio >= H2_THRESHOLD:
        return "Compatível (E/E_ref ≥ 10)"
    return "Contraria H2"


@dataclass
class Evaluation:
    """
    Resultado da avaliação dos modelos enviados.

    Atributos:
        summary        : uma linha por modelo (índice), com as mesmas colunas usadas
                         pelos gráficos do painel e as colunas da região escolhida.
        configurations : GMS de cada modelo em cada região (``n_modelos × 7``).
        k              : fator k de cada região, do menor para o maior.
        inversions     : pares em que um modelo mais caro supera um mais econômico.
        reference      : modelo de referência.
        context        : região escolhida.
    """

    summary: pd.DataFrame
    configurations: pd.DataFrame
    k: pd.Series
    inversions: pd.DataFrame
    reference: str
    context: str


def evaluate(
    runs: pd.DataFrame,
    reference: str,
    context_name: str = data.REFERENCE_CONTEXT,
    weights: Weights | None = None,
    contexts: Sequence[ExecutionContext] | None = None,
) -> Evaluation:
    """
    GMS, fronteira, custo frente à referência e regra D4 dos modelos enviados.

    Energia por modelo é a mediana entre as sementes e o F1 é a média, como no
    restante do painel. O GMS de cada região vem de ``evaluate_configurations`` da
    biblioteca, com as 7 regiões do ``contexts.csv``; carbono e água usam os
    fatores da região escolhida.
    """
    ctxs = list(contexts or data.load_contexts())
    weights = weights or data.make_weights(1, 1, 1)
    if reference not in set(runs.model):
        raise KeyError(f"Modelo de referência ausente: {reference}")
    ctx = next((c for c in ctxs if c.label == context_name), None)
    if ctx is None:
        raise KeyError(f"Região desconhecida: {context_name}")

    g = runs.groupby("model", sort=False)
    out = pd.DataFrame(
        {
            "f1_mean": g.f1.mean(),
            "f1_std": g.f1.std().fillna(0.0),
            "energy_mwh_mean": g.energy_kwh.mean() * data.KWH_TO_MWH,
            "energy_mwh_median": g.energy_kwh.median() * data.KWH_TO_MWH,
            "n_seeds": g.seed.nunique(),
        }
    )
    energy_kwh = out.energy_mwh_median / data.KWH_TO_MWH
    out["carbon_mg"] = [ctx.carbon_kg(e) * 1e6 for e in energy_kwh]
    out["water_ul"] = [ctx.water_l(e) * 1e6 for e in energy_kwh]

    ev = evaluate_configurations(energy_kwh.to_dict(), ctxs, weights=weights)
    cfg = ev.configurations.copy()
    k = data.k_factors(cfg, ctxs, weights)
    cfg["k"] = cfg.context.map(k)
    here = cfg[cfg.context == context_name].set_index("model")
    out["gms"] = here.gms
    out["rank_context"] = here.rank_gms
    out["rank_region"] = out.gms.rank(ascending=False, method="min").astype(int)

    ref = out.loc[reference]
    rel = [
        relative_to_reference(
            e,
            min(max(f, 0.0), 1.0),
            ref.energy_mwh_median / data.KWH_TO_MWH,
            ref.f1_mean,
            is_reference=(m == reference),
        )
        for m, e, f in zip(out.index, energy_kwh, out.f1_mean)
    ]
    out["energy_ratio_ref"] = [r.energy_ratio for r in rel]
    out["delta_f1_points"] = [r.delta_f1_points for r in rel]
    out["marginal_cost_j"] = [
        (
            None
            if math.isnan(r.marginal_cost_j_per_f1_point)
            else r.marginal_cost_j_per_f1_point
        )
        for r in rel
    ]
    out["pareto"] = ~pareto_dominated(
        out.energy_mwh_median.to_numpy(), out.f1_mean.to_numpy()
    )
    out["h2"] = [
        h2_reading(m == reference, p, r)
        for m, p, r in zip(out.index, out.pareto, out.energy_ratio_ref)
    ]
    return Evaluation(
        summary=out,
        configurations=cfg.reset_index(drop=True),
        k=k.sort_values(),
        inversions=data.inversions(cfg),
        reference=reference,
        context=context_name,
    )


def seed_points(runs: pd.DataFrame) -> pd.DataFrame:
    """Pontos por treinamento, no formato do gráfico de qualidade × custo."""
    return pd.DataFrame(
        {
            "model": runs.model,
            "seed": runs.seed,
            "energy_mwh": runs.energy_kwh * data.KWH_TO_MWH,
            "f1": runs.f1,
        }
    )


RESULT_COLUMNS: dict[str, str] = {
    "n_seeds": "treinamentos",
    "f1_mean": "f1_media",
    "f1_std": "f1_desvio",
    "energy_mwh_median": "energia_mwh_mediana",
    "carbon_mg": "carbono_mg_co2e",
    "water_ul": "agua_ul",
    "gms": "gms_na_regiao",
    "rank_context": "posicao_entre_configuracoes",
    "energy_ratio_ref": "e_sobre_e_ref",
    "delta_f1_points": "delta_f1_pontos",
    "marginal_cost_j": "custo_marginal_j_por_ponto_f1",
    "pareto": "na_fronteira_de_pareto",
    "h2": "regra_d4_h2",
}


def result_csv(evaluation: Evaluation, weights: Weights) -> bytes:
    """Resultado por modelo em CSV (``;`` e vírgula decimal), com região e pesos."""
    out = evaluation.summary[list(RESULT_COLUMNS)].rename(columns=RESULT_COLUMNS)
    out["na_fronteira_de_pareto"] = out.na_fronteira_de_pareto.map(
        {True: "sim", False: "não"}
    )
    out.insert(0, "modelo", out.index)
    out["referencia"] = evaluation.reference
    out["regiao"] = evaluation.context
    out["pesos_energia_carbono_agua"] = (
        f"{weights.w_E:.2f}/{weights.w_C:.2f}/{weights.w_W:.2f}".replace(".", ",")
    )
    return out.to_csv(sep=";", decimal=",", index=False, float_format="%.6g").encode(
        "utf-8-sig"
    )
