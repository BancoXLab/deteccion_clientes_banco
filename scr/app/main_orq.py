import pandas as pd
import threading
import platform
import psutil
import os
from typing import Dict, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prefect import flow, task, get_run_logger
from prefect.utilities.annotations import quote
from prefect.states import State
from model.model import predict_pipeline, __version__ as model_version

app = FastAPI(
    title="Banco X API (Prefect Integration)",
    description="API que predice si un cliente se suscribirá o no usando un modelo entrenado y registra la inferencia en Prefect",
    version=model_version
)

# ---- tasks de monitoreo ----
@task(name="Get System Metrics")
def get_system_metrics() -> Dict:
    """Obtener métricas del sistema."""
    try:
        process = psutil.Process(os.getpid())
        memory = psutil.virtual_memory()
        
        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "process_usage": process.memory_info().rss,
            },
            "disk": {
                "usage": psutil.disk_usage('/')._asdict()
            },
            "process": {
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections()),
            }
        }
    except Exception as e:
        return {"status": "error", "reason": str(e)}

@task(name="Check Model Status")
def check_model_status() -> Dict:
    """Verificar estado del modelo de predicción."""
    try:
        if model_version is None:
            return {"status": "error", "reason": "model_version_missing"}
        if not callable(predict_pipeline):
            return {"status": "error", "reason": "predict_pipeline_invalid"}
        return {"status": "ok", "model_version": model_version}
    except Exception as e:
        return {"status": "error", "reason": str(e)}

@task(name="Log Health Status")
def log_health_status(component: str, status: Dict):
    """Registrar estado de salud en Prefect."""
    logger = get_run_logger()
    logger.info(f"Health check - {component}: {status}")

@flow(name="Health Check Flow")
def health_check_flow() -> Dict:
    """Flow para verificar estado general del servicio."""
    model_status = check_model_status()
    system_metrics = get_system_metrics()
    
    log_health_status("model", model_status)
    log_health_status("system", system_metrics)
    
    return {
        "status": "ok" if model_status["status"] == "ok" else "degraded",
        "model": model_status,
        "system": system_metrics,
        "timestamp": datetime.now().isoformat()
    }

# ---- endpoints ----
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
    """Health check básico."""
    try:
        health_status = health_check_flow()
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/readyz")
def readyz() -> Dict:
    """Readiness check que verifica modelo y orquestación."""
    try:
        health_status = health_check_flow()
        if health_status["status"] != "ok":
            raise HTTPException(
                status_code=503, 
                detail={
                    "ready": False,
                    "reason": "health_check_failed",
                    "details": health_status
                }
            )
        return {"ready": True, "status": health_status}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"ready": False, "reason": str(e)}
        )

@app.get("/info")
def info() -> Dict:
    """Información del servicio, entorno y estado de Prefect."""
    try:
        model_status = check_model_status()
        return {
            "service": "Banco X API (Prefect Integration)",
            "model_version": model_version,
            "model_status": model_status["status"],
            "python": platform.python_version(),
            "prefect_enabled": True
        }
    except Exception as e:
        return {
            "service": "Banco X API (Prefect Integration)",
            "error": str(e),
            "python": platform.python_version(),
            "prefect_enabled": True
        }

# ---- modelo de datos ----
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


# ---- prefect flow ----
@task
def log_prediction_to_prefect(input_data: dict, prediction: float):
    logger = get_run_logger()
    logger.info("📦 Registrando inferencia en Prefect...")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info(f"Modelo: {model_version}")
    logger.info(f"Predicción: {prediction}")
    logger.info(f"Input: {input_data}")
    logger.info("✅ Registro completado.")


@flow(name="Flow de inferencia Banco X")
def inference_flow(input_data: dict, prediction: float):
    """Flow principal de inferencia que registra predicciones."""
    # Verificar salud antes de proceder
    health_status = check_model_status()
    if health_status["status"] != "ok":
        raise RuntimeError(f"Modelo no disponible: {health_status['reason']}")
    
    # Registrar predicción
    log_prediction_to_prefect(input_data, prediction)


# ---- endpoint ----
@app.post("/predict")
def predict(input_data: ClientData):
    try:
        # 🔹 conservar el input original como dict
        input_dict = input_data.dict()

        # 🔹 crear un DataFrame separado para el modelo
        input_df = pd.DataFrame([input_dict])

        # 🔹 hacer predicción
        prediction = predict_pipeline(input_df)
        prediction = float(prediction)  # asegurar que sea JSON-serializable

        # 🔹 lanzar Prefect flow en segundo plano
        threading.Thread(
            target=inference_flow,
            args=(input_dict, prediction)
        ).start()

        # 🔹 respuesta HTTP
        return {
            "prediction": prediction,
            "model_version": model_version,
        }

    except Exception as e:
        print(f"❌ Error interno en predict: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")