"""
run_analysis.py — Executa toda a análise da semana 4 sobre os resultados existentes.

Uso (após a execução completa):
    python experiments/run_analysis.py               # execuções full
    python experiments/run_analysis.py --mode quick_run

Para cada ``experiments/results/<dataset>/<modo>/`` (ignorando o legado ``_*``):
  1. ``statistical_analysis.py`` → ``stats_report.md``;
  2. ``generate_results.py`` → figuras e tabela em ``docs/Results/<dataset>/<modo>/``;
  3. ``context_analysis.py`` → avaliação modelo × contexto, se
     ``experiments/contexts/contexts.csv`` tiver ao menos um contexto (caso
     contrário, a etapa é pulada com aviso — nunca com valores inventados).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXTS = ROOT / "experiments" / "contexts" / "contexts.csv"


def _run(*args: str) -> None:
    cmd = [sys.executable, *args]
    print("$", " ".join(args), flush=True)
    subprocess.run(cmd, check=True, cwd=ROOT, stdout=subprocess.DEVNULL)


def contexts_defined(path: Path = CONTEXTS) -> bool:
    """True se o CSV de contextos tiver ao menos uma linha de dados."""
    if not path.exists():
        return False
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return len(lines) > 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--mode", default="full", choices=["full", "quick_run"])
    args = parser.parse_args()

    sys.path.insert(0, str(ROOT))
    from experiments.generate_results import discover

    runs = discover(args.mode)
    if not runs:
        sys.exit(f"Nenhuma execução '{args.mode}' em experiments/results.")
    use_contexts = contexts_defined()
    if not use_contexts:
        print(
            "[AVISO] experiments/contexts/contexts.csv sem contextos: "
            "a análise modelo × contexto será pulada."
        )
    for run in runs:
        rel = run.relative_to(ROOT) if run.is_absolute() else run
        print(f"\n=== {rel.as_posix()} ===")
        _run("experiments/statistical_analysis.py", str(rel))
        _run("experiments/generate_results.py", "--results", str(rel))
        if use_contexts:
            _run("experiments/context_analysis.py", str(rel))
    print("\n[OK] Análise concluída.")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
