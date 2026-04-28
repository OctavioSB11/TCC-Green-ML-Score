# GreenML Score Framework 🍃

O **GreenML Score** é um framework profissional e automatizado para medir, rastrear e reportar o impacto ambiental de modelos de Machine Learning.

Enquanto a maioria das bibliotecas foca apenas em Acurácia ou F1-Score (Red AI), o GreenML traz a sustentabilidade para o centro da tomada de decisão (Green AI), combinando o rastreamento em tempo real de hardware com uma métrica composta rigorosa.

## O que ele mede?
1. **Consumo Energético (kWh):** Obtido diretamente do rastreamento de Hardware (CPU via `psutil` e GPU via `pynvml`).
2. **Emissões de Carbono (kg CO2e):** Calculado com base na intensidade de carbono da matriz elétrica local.
3. **Pegada Hídrica (Litros):** Estimado pelo fator WUE (Water Usage Effectiveness) típico de data centers.

Tudo isso é condensado na métrica **GreenML Score (GMS)**, que varia de 0 a 100, onde valores maiores representam modelos mais sustentáveis e eficientes.

## 🚀 Instalação

```bash
# Clone o repositório e instale em modo editável com as dependências de desenvolvimento
git clone https://github.com/SeuUsuario/TCC-Green-ML-Score.git
cd TCC-Green-ML-Score
pip install -e .[dev]
```

## 💻 Como Usar (Fricção Zero)

O framework foi projetado para exigir o mínimo de alteração no seu código existente. Use os nossos **Wrappers** e **Callbacks**!

### Integração com Scikit-Learn

```python
import mlflow
from sklearn.ensemble import RandomForestClassifier
from green_ml_score.callbacks.sklearn import GreenMLSklearnWrapper
from green_ml_score.greenmlscore import NormalizationBounds

# 1. Defina seus limites máximos teóricos (para a normalização do GMS)
bounds = NormalizationBounds(energy_max=1.5, carbon_max=0.2, water_max=2.7)

# 2. Inicialize o MLflow
mlflow.set_experiment("GreenML_Demonstration")

with mlflow.start_run():
    # 3. Envolva seu modelo com o nosso Wrapper!
    base_model = RandomForestClassifier()
    green_model = GreenMLSklearnWrapper(base_model, bounds=bounds)
    
    # Ao chamar .fit(), o Tracker de Hardware liga automaticamente em background!
    # Quando o .fit() acaba, os resultados vão magicamente para o MLflow.
    green_model.fit(X_train, y_train)
```

## 📊 Visualizando Resultados

Por padrão, o framework usa o MLflow como plataforma de Dashboard.
Para visualizar o Score Ambiental e as métricas de hardware:

```bash
mlflow ui
```

Abra seu navegador em `http://127.0.0.1:5000` e veja a mágica acontecer!

## 🧪 Rodando Testes

O framework é coberto por testes unitários focados na validação rigorosa da matemática por trás do GMS.

```bash
pytest tests/
```
