import platform
import psutil
import os
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional
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
    return {"message": "La API está levantada y corriendo!", "model_version": model_version}

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

class ClientData(BaseModel):
    """Modelo mínimo de entrada. Acepta campos extra para compatibilidad.
    Si prefieres las validaciones avanzadas, restaura `scr.app.schemas.ClientData`.
    """
    model_config = {"extra": "allow"}
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request


@app.post("/predict")
def predict(input_data: ClientData) -> Dict[str, Any]:
    try:
        data_dict = input_data.model_dump()
        prediction = predict_pipeline(data_dict)
        return {
            "success": True,
            "prediction": float(prediction),
            "prediction_label": "Se suscribirá" if int(prediction) == 1 else "No se suscribirá",
            "model_version": model_version,
            "timestamp": datetime.now().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail={
            "error": "Error en los datos de entrada",
            "message": str(e),
            "status": "VALIDATION_ERROR",
            "timestamp": datetime.now().isoformat()
        })
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail={
            "error": "Error en la predicción",
            "message": str(e),
            "status": "PREDICTION_ERROR",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "Error inesperado",
            "message": str(e),
            "status": "INTERNAL_ERROR",
            "timestamp": datetime.now().isoformat()
        })


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = ".".join([str(x) for x in err.get("loc", []) if x not in ("body",)])
        msg = err.get("msg")
        err_type = err.get("type")
        friendly = msg
        if err_type and "type_error" in err_type:
            friendly = f"Tipo inválido para '{loc}': {msg}"
        elif err_type and "value_error" in err_type:
            friendly = f"Valor inválido para '{loc}': {msg}"
        errors.append({"field": loc, "message": friendly, "raw": err})

    return JSONResponse(status_code=422, content={
        "success": False,
        "error": "Validación de datos fallida",
        "details": errors,
        "status": "VALIDATION_ERROR",
        "timestamp": datetime.now().isoformat(),
        "hint": "Revisa los campos señalados y verifica tipos y rangos."
    })