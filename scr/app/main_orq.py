import platform
import psutil
import os
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from prefect import flow, task, get_run_logger
from scr.app.model.model import predict_pipeline, __version__ as model_version
from scr.app.routes.general_routes import router as general_router

app = FastAPI(
    title="Banco X API (Prefect Integration)",
    description="API que predice si un cliente se suscribirá o no usando un modelo entrenado y registra la inferencia en Prefect",
    version=model_version
)

app.include_router(general_router)

# Prefect
@task(name="Get System Metrics")
def get_system_metrics() -> Dict:
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
                "connections": len(process.net_connections()),
            }
        }
    except Exception as e:
        return {"status": "error", "reason": str(e)}

@task(name="Check Model Status")
def check_model_status() -> Dict:
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
    logger = get_run_logger()
    logger.info(f"Health check - {component}: {status}")

@flow(name="Health Check Flow")
def health_check_flow() -> Dict:
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

# ---- Endpoints Prefect ----
@app.get("/")
def home() -> Dict:
    return {"message": "✅ La API está levantada y corriendo!", "model_version": model_version}

@app.get("/healthz")
def healthz() -> Dict:
    try:
        health_status = health_check_flow()
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/readyz")
def readyz() -> Dict:
    try:
        health_status = health_check_flow()
        if health_status["status"] != "ok":
            raise HTTPException(status_code=503, detail={
                "ready": False, "reason": "health_check_failed", "details": health_status
            })
        return {"ready": True, "status": health_status}
    except Exception as e:
        raise HTTPException(status_code=503, detail={"ready": False, "reason": str(e)})

@app.get("/info")
def info() -> Dict:
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
    
# ---- Validador general para todos los campos ----
@field_validator("*", mode="before")
def validar_tipos(cls, value: Any, info):
    """Valida tipos antes de parsear, con mensaje personalizado."""
    field_name = info.field_name

    if value is None:
        raise ValueError(f"El campo '{field_name}' no puede ser nulo.")

    # Validar tipo esperado por nombre de campo
    if field_name in ["month", "day_of_week", "previous_bin",
                          "marital_divorced", "marital_married", "marital_single", "marital_unknown",
                          "housing_no", "housing_unknown", "housing_yes",
                          "loan_no", "loan_unknown", "loan_yes",
                          "contact_cellular", "contact_telephone"]:
        if not isinstance(value, int):
            raise TypeError(f"El campo '{field_name}' debe ser un número entero (int).")
    else:
        if not isinstance(value, (float, int)):
            raise TypeError(f"El campo '{field_name}' debe ser un número decimal (float).")

    return value