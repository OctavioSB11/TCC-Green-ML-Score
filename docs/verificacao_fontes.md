# Verificação das fontes citadas (etapa 4, 17/10/2026)

Escopo: `docs/TCC_GreenML_Score_revisado.docx` (valores de intensidade de carbono, WUE e
PUE, Desislavov et al. e as referências novas) e `experiments/contexts/contexts.csv`.
Todas as consultas foram feitas em 17/10/2026, em fontes gratuitas. Status: **Confere**
(o número e a referência batem com a fonte), **Corrigido** (erro claro, já ajustado no
`.docx` revisado) e **Dúvida** (não foi possível confirmar; decisão da dupla).

## 1. Tabela de verificação

| # | Citação (onde) | Valor no texto | Valor na fonte | URL | Status |
|---|---|---|---|---|---|
| 1 | Tabela 1, Google Cloud (GOOGLE, 2024) | PUE 1,10 | 1,10: média anual de 2023, publicada no Environmental Report de 2024 (em 2024, 1,09) | https://blog.google/outreach-initiatives/sustainability/2024-environmental-report/ ; https://www.google.com/about/datacenters/efficiency/ | Confere. Acrescentada à fonte da tabela a nota "Google: média de 2023, publicada em 2024" |
| 2 | Tabela 1, AWS | PUE 1,15 | 1,15: PUE global de 2024 (e de 2023); 1,14 em 2025 | https://sustainability.aboutamazon.com/environment/the-cloud | Confere. **Resolvido**: a referência inexistente "Sustainability in the cloud report 2024" foi substituída por AMAZON ([2026]), página "AWS Cloud", que publica o valor |
| 3 | Tabela 1, Microsoft Azure (MICROSOFT, 2024) | PUE médio 1,12 | 1,12 é o PUE **de projeto** da geração mais recente; a média global publicada é 1,16 (ano fiscal 2024) e 1,17 (ano fiscal 2025) | https://datacenters.microsoft.com/sustainability/efficiency/ ; https://azure.microsoft.com/en-us/blog/sharing-the-latest-improvements-to-efficiency-in-microsoft-s-datacenters/ | **Corrigido**: 1,16, com nota na fonte da tabela e nova referência MICROSOFT ([2026]) |
| 4 | Tabela 1, média da indústria (UPTIME INSTITUTE, 2024) | PUE 1,56 | 1,56 (Global Data Center Survey 2024; média declarada pelos respondentes para seu maior data center) | https://intelligence.uptimeinstitute.com/resource/uptime-institute-global-data-center-survey-2024 ; https://www.datacenterknowledge.com/energy-power-supply/data-center-industry-survey-highlights-cost-ai-and-sustainability-challenges | Confere. Sugestão: acrescentar URL à referência |
| 5 | Seção 5.4, IC do cenário de referência | 120 gCO₂e/kWh (IEA) → **106,06 gCO₂/kWh** | Ember, Brasil, 2024: 106,06 gCO₂/kWh (mesma fonte do contexts.csv; o BR-local usa 2025, 109,95). O valor da IEA não era verificável (produto pago e descontinuado) | https://ember-energy.org/data/yearly-electricity-data/ | **Resolvido** (decisão da dupla, 17/10): `experiments/config.py`, README, `example_run.py`, teste e texto da 5.4; referência da IEA removida, pois nada mais a cita |
| 6 | Seção 5.4, WUE do cenário de referência | 0,52 L/kWh ("Google") → **0,30 L/kWh** | Microsoft, média global do ano fiscal de 2024: 0,30 L/kWh. Nenhuma fonte para 0,52 atribuído ao Google foi encontrada | https://datacenters.microsoft.com/sustainability/efficiency/ | **Resolvido** (decisão da dupla, 17/10): `experiments/config.py`, README, `example_run.py`, docstring de `water.py`, teste e texto da 5.4, citando MICROSOFT ([2026]) |
| 7 | Seção 1.1 e referências, Desislavov, Martínez-Plumed e Hernández-Orallo (2023) | Referência: "Trends in AI inference energy consumption", v. 38, 2023 | Título completo: "Trends in AI inference energy consumption: beyond the performance-vs-parameter laws of deep learning", Sustainable Computing: Informatics and Systems, v. 38, art. 100857, abr. 2023 | https://doi.org/10.1016/j.suscom.2023.100857 ; https://arxiv.org/abs/2109.05472 | **Corrigido** (título, artigo, mês e DOI). A afirmação do texto (a inferência pode responder pela maior parte do consumo) é coerente com a motivação do artigo; conferir no texto publicado |
| 8 | Seção 8.4 e Tabela 3, EMBER (2026) | BR 109,95; FR 41,45; IN 670,55; DE 329,65; SE 35,35; Virgínia 356,59 gCO₂e/kWh (2025) | Os mesmos valores nos arquivos `yearly_full_release_long_format.csv` (países) e `release_us_subnational_generation_yearly.csv` (Virgínia, 356,592) | https://ember-energy.org/data/yearly-electricity-data/ ; https://ember-energy.org/data/us-electricity-data/ | Confere. Dúvida menor: o arquivo global rotula a unidade como gCO₂/kWh, e o texto usa gCO₂e/kWh |
| 9 | Seção 8.4 e Tabela 3, AMAZON WEB SERVICES (2026) | PUE/WUE 2025: São Paulo 1,14/0,09; Virgínia 1,15/0,06; Frankfurt 1,24/0,17; Estocolmo 1,09/0,02; Paris e Mumbai sem WUE | Os mesmos valores nas fichas de sustentabilidade (Paris: PUE 1,35, WUE "--"; Mumbai: PUE 1,40, sem WUE) | https://sustainability.aboutamazon.com/aws-sustainability-fact-sheets/aws-fact-sheet-brazil.pdf (idem `-virginia`, `-germany`, `-sweden`, `-france`, `-india`) | Confere. **Corrigido**: a referência passou a listar também France e India, citadas na afirmação sobre Paris e Mumbai |
| 10 | Seção 8.4 e Tabela 3, Reig et al. (2020) | Água off-site: BR 18,58; FR 3,67; IN 3,44; DE 1,93; SE 6,02; Virgínia 2,38 L/kWh | Apêndice 2: Brasil 4,91; França 0,97; Índia 0,91; Alemanha 0,51; Suécia 1,59 gal/kWh; Apêndice 1: SRVC 0,63 gal/kWh; × 3,785 L/gal. EUA, SRVC, Suécia e Índia coincidem com a Tabela 1 de Li et al. | https://files.wri.org/d8/s3fs-public/guidance-calculating-water-use-embedded-purchased-electricity_0.pdf | Confere |
| 11 | Seção 2.2, Li et al. (2023) | arXiv:2304.03271, 2023 | arXiv:2304.03271 (v1 de 2023; v5 de mar. 2025); versão publicada na Communications of the ACM (2025) | https://arxiv.org/abs/2304.03271 ; https://dl.acm.org/doi/10.1145/3724499 | Confere. Sugestão: citar a versão publicada |
| 12 | Referência GOOGLE (2024) | "Google data centers: efficiency and PUE reporting 2024" | O PUE de 1,10 está no 2024 Environmental Report | https://www.gstatic.com/gumdrop/sustainability/google-2024-environmental-report.pdf | **Resolvido**: referência substituída por GOOGLE. 2024 Environmental Report (2024) |

## 2. Resumo

- **Conferem (8):** Google 1,10; AWS 1,15; Uptime 1,56; Ember 2025 (6 contextos); fichas da AWS
  (4 regiões e a ausência de WUE em Paris e Mumbai); Reig et al. (6 fatores); Li et al.;
  afirmação geral de Desislavov et al.
- **Corrigidos no `.docx` revisado (4):** Microsoft 1,12 → 1,16, com nota e nova referência;
  nome do produto da IEA ("Emissions Factors 2024"; referência depois removida, ver abaixo); referência de Desislavov et al.
  completa; referência das fichas da AWS com France e India.
- **Resolvidos por decisão da dupla (17/10/2026), 4:** IC do cenário de referência
  (120, IEA → 106,06, Ember 2024); WUE (0,52, "Google" → 0,30, Microsoft FY24); referência
  AWS 2024 → AMAZON ([2026]); referência GOOGLE 2024 → 2024 Environmental Report. A
  referência da IEA saiu da lista, pois nada mais a cita.
- **Dúvida restante, 1:** unidade gCO₂ × gCO₂e da Ember (item 8).

Observação sobre o impacto: a troca de IC e WUE não altera nenhum número do texto. O GMS
de contexto único depende só da energia quando IC e WUE são constantes (seção 4.3), e a
análise regenerada (`run_analysis.py`) produziu os mesmos relatórios e figuras. Ressalva:
as colunas `carbon_kg` e `water_liters` dos `comparative_results.csv`, os cartões
ambientais e o `run_metadata.json` da execução completa foram gravados com os valores
antigos (120 e 0,52), pois os resultados não podem ser editados à mão e o experimento não
foi refeito. Esses valores não são citados no texto; se forem usados, devem ser
recalculados (C = E × 106,06 / 1000; W = E × 0,30) ou o experimento deve ser repetido.

## 3. Checklist para o integrante B: conferência de `experiments/contexts/contexts.csv`

Esta verificação não substitui a conferência independente das fontes de contexto.

- [ ] Abrir o arquivo anual da Ember (`yearly_full_release_long_format.csv`) e conferir, para
      2025 e a variável "CO2 intensity", Brasil 109,95; França 41,45; Índia 670,55;
      Alemanha 329,65; Suécia 35,35.
- [ ] Abrir o arquivo dos EUA (`release_us_subnational_generation_yearly.csv`) e conferir
      Virgínia, "Total generation", 2025: 356,592 gCO₂e/kWh.
- [ ] Decidir se o texto usa gCO₂/kWh ou gCO₂e/kWh para a Ember (ver item 8).
- [ ] Abrir as fichas da AWS (Brazil, Virginia, Germany, Sweden) e conferir o PUE e o WUE
      de 2025; confirmar que France e India não publicam WUE.
- [ ] Abrir o working paper do WRI (Reig et al., 2020) e conferir, no Apêndice 2, Brasil
      4,91; França 0,97; Índia 0,91; Alemanha 0,51; Suécia 1,59 gal/kWh e, no Apêndice 1,
      SRVC 0,63 gal/kWh; refazer a conversão por 3,785 L/gal.
- [ ] Conferir que os contextos locais (`*-local`) têm PUE = 1 e WUE = 0 e que cada linha do
      CSV tem fonte e data de acesso.
- [ ] Conferir `contexts_pendentes.csv` (AWS Paris e Mumbai sem WUE; IC horária do SIN).
- [ ] Registrar em `docs/revisao.md` a data da conferência e quem a fez.
