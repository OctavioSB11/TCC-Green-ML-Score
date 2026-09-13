# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

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
