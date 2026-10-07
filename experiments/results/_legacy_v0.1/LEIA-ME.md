# Resultados legados (v0.1) — NÃO usar no texto final

Preservados apenas para rastreabilidade da revisão metodológica.

- `newsgroups_3seeds/`: execução que fundamenta a Seção 8 da versão .docx
  (3 sementes, treino+predição medidos juntos, n_jobs diferente entre modelos,
  coluna "GreenML Score (US)" idêntica à "(BR)").
- `newsgroups_3seeds/emissions_codecarbon_raw.csv`: log bruto do CodeCarbon
  (Windows 11, i5-1235U, tracking_mode = machine, RAM fixa em 20 W).
- `quick_runs/`: execuções de validação (500 amostras, 1 semente) — sem valor estatístico.

Os resultados válidos são gerados pelo protocolo revisado em
`experiments/results/<dataset>/<modo>/`.
