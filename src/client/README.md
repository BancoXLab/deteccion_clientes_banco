# Cliente API - Banco X

Cliente Python para consumir la API de predicción de suscripción de clientes del Banco X.

## 📋 Descripción

El cliente `APIClient` proporciona una interfaz simple y robusta para interactuar con la API de predicción. La API ejecuta un modelo de machine learning que predice si un cliente se suscribirá o no a un producto bancario.

## 🚀 Uso básico

### Instalación de dependencias

```bash
pip install requests
```

### Ejemplo simple

```python
from scr.client.client import APIClient

# Crear cliente
client = APIClient("http://localhost:8000")

# Datos del cliente (27 campos requeridos)
data = {
    "age": 35,
    "month": 5,
    "day_of_week": 1,
    "duration": 500,
    "campaign": 1,
    "pdays": -1,
    "previous": 0,
    "emp_var_rate": 1.1,
    "cons_price_idx": 93.5,
    "cons_conf_idx": -36.0,
    "euribor3m": 0.7,
    "nr_employed": 5100.0,
    "previous_bin": 0,
    "job_target_mean": 0.45,
    "marital_divorced": 0,
    "marital_married": 1,
    "marital_single": 0,
    "marital_unknown": 0,
    "education_freq_encode": 0.5,
    "housing_no": 0,
    "housing_unknown": 0,
    "housing_yes": 1,
    "loan_no": 0,
    "loan_unknown": 0,
    "loan_yes": 1,
    "contact_cellular": 1,
    "contact_telephone": 0,
}

# Realizar predicción
try:
    result = client.predict(data)
    print(f"Predicción: {result.prediction_label}")
    print(f"Confianza: {result.prediction:.2%}")
except Exception as e:
    print(f"Error: {e}")
```

## 📚 Métodos disponibles

### `predict(payload, timeout=10)`

Realiza una predicción usando los datos del cliente.

**Parámetros:**
- `payload` (dict): Diccionario con 27 campos del cliente
- `timeout` (int): Segundos de espera máxima (default: 10s)

**Retorna:**
- `PredictionResponse`: Objeto con la predicción y metadata

**Campos requeridos en payload:**
- Demográficos: `age`, `month`, `day_of_week`
- Contacto: `duration`, `campaign`, `pdays`, `previous`, `contact_cellular`, `contact_telephone`
- Económicos: `emp_var_rate`, `cons_price_idx`, `cons_conf_idx`, `euribor3m`, `nr_employed`
- Históricos: `previous_bin`, `job_target_mean`
- Categorías (one-hot encoded):
  - Estado civil: `marital_divorced`, `marital_married`, `marital_single`, `marital_unknown`
  - Vivienda: `housing_no`, `housing_unknown`, `housing_yes`
  - Préstamo: `loan_no`, `loan_unknown`, `loan_yes`
  - Educación: `education_freq_encode`

### `health_check(timeout=5)`

Verifica que la API esté operacional.

**Parámetros:**
- `timeout` (int): Segundos de espera máxima (default: 5s)

**Retorna:**
- dict: Estado de salud del servicio

```python
status = client.health_check()
print(status)  # {'status': 'ok', ...}
```

### `get_info(timeout=5)`

Obtiene información general del servicio (versión, modelo, etc.).

**Parámetros:**
- `timeout` (int): Segundos de espera máxima (default: 5s)

**Retorna:**
- dict: Información del servicio

```python
info = client.get_info()
print(info["model_version"])
```

## 🔍 Objeto PredictionResponse

Respuesta estructurada de una predicción:

```python
result = client.predict(data)

# Acceder a los campos
result.success              # bool: Predicción exitosa
result.prediction           # float: Score de predicción (0-1)
result.prediction_label     # str: Etiqueta legible ("Se suscribirá" / "No se suscribirá")
result.model_version        # str: Versión del modelo utilizado
result.timestamp            # str: ISO timestamp de la predicción
result.raw_response         # dict: Respuesta cruda de la API
```

## ⚠️ Manejo de errores

```python
import requests
from scr.client.client import APIClient

client = APIClient()

try:
    result = client.predict(data)
except requests.ConnectionError:
    print("No se pudo conectar a la API")
except ValueError as e:
    print(f"Error de validación o respuesta: {e}")
except requests.Timeout:
    print("Timeout: la API tardó demasiado en responder")
except requests.RequestException as e:
    print(f"Error de request: {e}")
```

## 🧪 Ejecutar cliente de prueba

```bash
cd /workspaces/deteccion_clientes_banco
python -m scr.client.client
```

Esto ejecutará el cliente con datos de ejemplo y mostrará:
- ✅ Estado de salud de la API
- 📊 Información del servicio
- 🔮 Una predicción de ejemplo

## 🔗 Endpoints disponibles en la API

El cliente consume los siguientes endpoints:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/predict` | POST | Realiza una predicción |
| `/healthz` | GET | Verifica salud del servicio |
| `/readyz` | GET | Verifica disponibilidad de la API |
| `/info` | GET | Información del servicio |
| `/` | GET | Mensaje de bienvenida |

## 📝 Integración en aplicaciones

### Con Flask/FastAPI

```python
from fastapi import FastAPI
from scr.client.client import APIClient

app = FastAPI()
api_client = APIClient("http://prediction-api:8000")

@app.post("/v1/subscribe-prediction")
async def get_prediction(customer_data: dict):
    try:
        result = api_client.predict(customer_data)
        return {
            "will_subscribe": result.prediction_label,
            "confidence": result.prediction
        }
    except Exception as e:
        return {"error": str(e)}, 500
```

### Con Pandas DataFrame

```python
import pandas as pd
from scr.client.client import APIClient

client = APIClient()
df = pd.read_csv("customers.csv")

# Realizar predicciones para múltiples clientes
predictions = []
for _, row in df.iterrows():
    try:
        result = client.predict(row.to_dict())
        predictions.append(result.prediction)
    except Exception as e:
        print(f"Error para cliente {row.get('id')}: {e}")
        predictions.append(None)

df["prediction"] = predictions
```

## 🔧 Configuración

### Variables de entorno (recomendado)

```bash
export BANCO_X_API_URL="http://prediction-api:8000"
```

```python
import os
from scr.client.client import APIClient

api_url = os.getenv("BANCO_X_API_URL", "http://localhost:8000")
client = APIClient(api_url)
```

## ✨ Características

✅ Cliente typado con dataclass `PredictionResponse`
✅ Manejo robusto de errores HTTP
✅ Documentación completa en docstrings
✅ Soporte para timeout configurable
✅ Métodos auxiliares (health_check, get_info)
✅ Script de prueba integrado
✅ Compatible con main.py, main_orq.py y routes

## 📞 Soporte

Para problemas o sugerencias, contacta al equipo de ML.
