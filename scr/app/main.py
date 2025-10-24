from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import platform

from model.model import predict_pipeline, __version__ as model_version

app = FastAPI(
    title="Banco X API",
    description="API que predice si un cliente se suscribirá o no usando un modelo entrenado",
    version=model_version,
)

# Modelo de datos de entrada (sin 'y' — la target)
class ClientData(BaseModel):
    age: float
    month: int
    day_of_week: int
    duration: float
    campaign: float
    pdays: float
    previous: float
    emp_var_rate: float
    cons_price_idx: float
    cons_conf_idx: float
    euribor3m: float
    nr_employed: float
    previous_bin: int
    job_target_mean: float
    marital_divorced: int
    marital_married: int
    marital_single: int
    marital_unknown: int
    education_freq_encode: float
    housing_no: int
    housing_unknown: int
    housing_yes: int
    loan_no: int
    loan_unknown: int
    loan_yes: int
    contact_cellular: int
    contact_telephone: int


def _is_model_ready() -> bool:
    """Chequear de forma ligera si el modelo está disponible.
    Evitamos llamadas de predicción aquí para no cargar recursos; comprobamos
    que exista una versión y que la función de predicción sea callable.
    """
    try:
        if model_version is None:
            return False
        return callable(predict_pipeline)
    except Exception:
        return False


@app.get("/")
def home() -> Dict:
    return {
        "message": "✅ La API está levantada y corriendo!",
        "model_version": model_version,
    }


@app.get("/ping")
def ping() -> Dict:
    """Endpoint simple para comprobación rápida de latencia/respuesta."""
    return {"ping": "pong"}


@app.get("/healthz")
def healthz() -> Dict:
    """Health check básico: responde 200 si la app está corriendo."""
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> Dict:
    """Readiness: indica si el servicio está listo para recibir tráfico productivo.
    Comprueba de forma liviana si el modelo parece estar disponible.
    Devuelve 200 si listo, 503 si no.
    """
    if _is_model_ready():
        return {"ready": True, "model_version": model_version}
    else:
        raise HTTPException(status_code=503, detail={"ready": False, "reason": "model_unavailable"})


@app.get("/info")
def info() -> Dict:
    """Información del servicio y entorno."""
    return {
        "service": "Banco X API",
        "model_version": model_version,
        "python": platform.python_version(),
    }


@app.post("/predict")
def predict(input_data: ClientData):
    try:
        prediction = predict_pipeline(input_data.dict())
        return {
            "prediction": prediction,
            "model_version": model_version,
        }
    except ValueError as e:
        # datos de entrada incompletos / mal formados
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        # errores durante la predicción o mismatch con el modelo
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # catch-all
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
 