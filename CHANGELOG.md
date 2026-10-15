# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Não lançado] — análise, figuras e tabelas (semana 4)

### Alterado (15/10)
- Dominância passa a ser de Pareto (F1 × energia) entre todos os modelos da mesma semente (`pareto_dominated`); antes, bastava ΔF1 ≤ 0 em relação à referência. A posição em relação à referência é registrada em `position_vs_ref`.

### Adicionado
- `experiments/run_analysis.py`: executa estatística, figuras e análise de contextos para todas as execuções de um modo.
- `context_analysis.py`: figuras `context_gms_heatmap` (GMS modelo × contexto) e `context_simplex` (τ_b e configuração vencedora no simplex de pesos).
- `statistical_analysis.py`: testes pareados também sobre a energia, score relativo, energia líquida, repetições efetivas e avisos de `run_metadata.json`.

### Alterado
- `generate_results.py` reescrito: figuras de energia (bruta e líquida, escala log) e tempo, F1 × energia com fronteira de Pareto, GMS com nota de degeneração; tabela LaTeX e README a partir dos dados (sem número de sementes, limites de eixo ou "região ótima" fixos); diretórios de legado (`_*`) não são mais reprocessados.
- Figuras de quick-run (`docs/Results/*/quick_run/`) deixam de ser versionadas.

### Removido
- `experiments/sensitivity_analysis.py` (substituído pelo módulo `contexts`) e o gráfico de radar (com IC e WUE constantes, carbono e água repetiam a energia).

## [Não lançado] — preparação da execução completa (semana 3)

### Adicionado
- `experiments/energy_validation.py`: validação física do CodeCarbon sem custo, pela descarga da bateria do notebook lida via WMI (potência de descarga integrada e queda da carga restante); fases de repouso e carga; comparação da energia incremental. Medidor de tomada mantido como fonte opcional (`--source meter`). Substitui `meter_validation.py`.
- `docs/execucao_completa.md`: roteiro da execução completa (preparação da máquina, comandos, tempos estimados, critérios de descarte).

## [Não lançado] — revisão metodológica (semana 2)

### Adicionado
- Módulo `green_ml_score.contexts`: `ExecutionContext` (IC, PUE, WUE on-site, fator hídrico off-site, horário), leitura de contextos via CSV, avaliação modelo × contexto com GMS sobre limites globais, τ_b de Kendall entre os rankings do GMS e da energia e varredura no simplex de pesos.
- `experiments/context_analysis.py` e modelo vazio `experiments/contexts/contexts.csv`.
- `green_ml_score.scoring.relative`: razão de energia, custo marginal (J por ponto de F1) e dominância em relação a um modelo de referência.
- `green_ml_score.reporting.EnvironmentalCard`: cartão ambiental por modelo em Markdown.
- `ProvenanceWarning` e `provenance_warnings_for()`: avisos de modo `machine`, RAM constante e RAM > 50 % da energia.
- Experimento: medição de repouso (P₀) e energia líquida E − P₀·t, aquecimento descartado por modelo, score relativo pareado por semente e cartões por modelo.

### Corrigido
- Fases curtas eram dominadas pelo overhead fixo do CodeCarbon (≈ 1,5 s e dezenas de J por sessão). Cada fase agora é repetida até uma janela mínima (`MIN_MEASUREMENT_WINDOW_S`), e o número efetivo de repetições é registrado.

## [Não lançado] — revisão metodológica (semana 1)

### Corrigido
- Falha na leitura da energia retornava 0,0 kWh em silêncio (GMS = 100 espúrio); agora lança `MeasurementError`.
- Experimento media treino e predição juntos, com `n_jobs` diferente entre modelos e acurácia de um modelo distinto do medido.
- Cenário "EUA" apenas reescalava os limites de normalização e produzia GMS idêntico ao cenário BR; removido.
- Fallbacks silenciosos para dados sintéticos quando o download de datasets falhava; removidos.
- Energia rotulada como μWh era mWh (erro de fator 1.000).
- README de resultados com números e conclusões digitados manualmente; agora gerado a partir dos dados.
- Resultados de cada dataset sobrescreviam os anteriores; agora gravados em `results/<dataset>/<modo>/`.
- MLflow registrava GMS calculado com limite fixo de 1 kWh; GMS só é registrado com limites definidos.

### Adicionado
- `MeasurementDetails`: procedência da medição (modo do CodeCarbon, potências, fração de energia da RAM).
- `experiments/statistical_analysis.py` (Friedman, Wilcoxon-Holm, Spearman, checagem de degeneração).
- `tests/test_gms_properties.py`: especificação formal de que GMS = E_norm sob IC/WUE constantes.
- `run_metadata.json` por execução (commit, plataforma, configuração).

## [0.1.0] - 2026-09-09

### Adicionado
- **Arquitetura modular do framework core em 4 camadas**:
  - `collectors`: adaptadores e instrumentação de hardware para coleta de dados ambientais em tempo real.
  - `estimators`: conversão analítica de consumo elétrico para pegada de carbono e consumo hídrico.
  - `scoring`: núcleo puro de cálculo da métrica GreenML Score (GMS), normalização e explicabilidade.
  - `integrations`: conectores de interoperabilidade para frameworks de Machine Learning e plataformas de MLOps.
- **Métrica composta GreenML Score (GMS)**:
  - Implementação da função `calculate_gms` com normalização min-max inversa $X_{\text{norm}} = 1 - (X / X_{\text{max}})$, assegurando que menores impactos ambientais resultem em maiores pontuações.
  - Estrutura de pesos contextuais configuráveis (`Weights`: $w_E, w_C, w_W$) com validação de soma unitária ($1.0$) e limites não negativos, permitindo modelar cenários de estresse hídrico ou matrizes de alta intensidade de carbono.
  - Modelos de dados com dataclasses `EnvironmentalMetrics` e `NormalizationBounds`.
  - Método estático `NormalizationBounds.from_metrics_list` para cálculo dinâmico dos limites de normalização a partir do conjunto de medições experimentais.
  - Função `explain_gms` para decomposição analítica e explicabilidade das contribuições de cada dimensão no score final.
  - Suporte ao argumento `scale_100=True` para escalonamento operacional do score para a escala $[0, 100]$.
- **Instrumentação e monitoramento de hardware via CodeCarbon**:
  - Implementação do coletor `GreenMLTracker` integrando o `EmissionsTracker` do CodeCarbon para medição em tempo real de hardware (RAPL para Intel CPUs e NVML para NVIDIA GPUs).
  - Estratégia de leitura resiliente de energia consumida a partir do arquivo `emissions.csv`, garantindo consistência operacional entre diferentes versões da biblioteca CodeCarbon.
- **Módulo de estimativa de emissões de carbono**:
  - Função `calculate_carbon_emissions` baseada na formulação $C = E \times \text{IC}_{\text{região}}$, permitindo parametrizar a intensidade de carbono da matriz elétrica regional em gCO2e/kWh (com valores de referência para Brasil/SP, EUA, União Europeia, China e Índia).
- **Módulo de estimativa de pegada hídrica**:
  - Função `calculate_water_usage` para mensuração indireta da água consumida em data centers através do proxy $W \approx E \times \text{WUE}$ (*Water Usage Effectiveness*), parametrizável com coeficientes de data centers de referência (ex.: Google Cloud 2024 $\approx 0.52\text{ L/kWh}$, Azure $\approx 1.1\text{ L/kWh}$, média de mercado $\approx 1.8\text{ L/kWh}$).
- **Wrapper não intrusivo para Scikit-Learn**:
  - Classe `GreenMLSklearnWrapper` para encapsular estimadores e pipelines compatíveis com o padrão do scikit-learn, automatizando o acionamento do `GreenMLTracker` no método `.fit()`.
  - Encaminhamento e delegação dinâmica de chamadas (`predict`, `predict_proba`, atributos) para o modelo base subjacente.
- **Integração com plataforma MLflow**:
  - Função `log_greenml_run` para logging automático em execuções ativas do MLflow, registrando métricas ambientais (`greenml_energy_kwh`, `greenml_carbon_kg`, `greenml_water_liters`), parâmetros de contexto operacional e a métrica `GreenML_Score`.
- **Protocolo de experimentos comparativos**:
  - Pipeline de experimentação comparando 4 arquiteturas de modelos de Machine Learning (Regressão Logística, Random Forest, Rede Neural MLP e XGBoost) no dataset de análise de sentimento *IMDb Movie Reviews* com vetorização TF-IDF.
  - Avaliação robusta com protocolo multi-semente (sementes 42, 123 e 2024) para mensuração de média e desvio padrão.
- **Visualizações gráficas científicas**:
  - Gráfico de barras horizontais (*Bar Chart*) com o ranking de sustentabilidade pelo GreenML Score médio e barras de dispersão de erro ($\pm \sigma$).
  - Gráfico de dispersão e fronteira de Pareto (*Scatter Plot*): Acurácia Preditiva vs. GreenML Score, delimitando o quadrante ideal de sustentabilidade (*Green AI*).
  - Gráfico de radar multidimensional (*Spider Chart*) contemplando 5 eixos normalizados: Acurácia, F1-Score, Eficiência Energética, Baixo Carbono e Baixo Consumo Hídrico.
  - Gráfico de barras comparativo direto entre Consumo Energético ($\mu\text{Wh}$) e Tempo de Treinamento ($s$).
  - Exportação automatizada das figuras em resolução de publicação acadêmica (PNG 300 DPI e SVG vetorial).
- **Tabela formatada em LaTeX para o TCC**:
  - Script gerador de tabela formal LaTeX com a biblioteca `booktabs` (`summary_table.tex`), pronta para inclusão direta no artigo acadêmico e na monografia do TCC.
- **Suíte de testes de unidade automatizados**:
  - 32 testes unitários implementados com `pytest`, cobrindo 100% dos fluxos matemáticos do GreenML Score, estimadores ambientais, tratamento de valores limites/exceções, ciclo de vida do tracker e integrações com Scikit-Learn e MLflow.
- **Esteira de Integração Contínua (CI/CD)**:
  - Fluxo de trabalho automatizado no GitHub Actions (`.github/workflows/ci.yml`) com matriz de compatibilidade em Python 3.10, 3.11, 3.12 e 3.13.
  - Etapas de validação de qualidade de código e estilo com Ruff, verificação estrita de formatação com Black e testes automatizados com relatório de cobertura via `pytest-cov`.
- **Licença de código aberto**:
  - Adoção da licença MIT permissiva para o projeto, sob autoria de Octavio Bordotti e Danilo Parolin.

[0.1.0]: https://github.com/OctavioSB11/TCC-Green-ML-Score/releases/tag/v0.1.0
