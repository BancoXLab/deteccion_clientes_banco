import platform
import psutil
import os
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from prefect import flow, task, get_run_logger
from src.app.model.model import predict_pipeline, predict_pipeline_proba, __version__ as model_version
from src.app.routes.general_routes import router as general_router

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


@app.post("/predict")
async def predict(input_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predice para múltiples clientes y devuelve solo los con clase=1 (suscripción positiva).
    Cada cliente puede tener un 'client_id' opcional para trackeo.
    
    Input: lista de objetos con campos del modelo + 'client_id' opcional.
    Output: lista de predicciones con clase=1, ordenadas por probabilidad descendente.
    """
    try:
        results = []
        
        for idx, client in enumerate(input_data):
            try:
                # client es un Dict, no un Pydantic model
                client_id = client.pop("client_id", idx)  # usar client_id si existe, sino index
                data_dict = client.copy()  # hacer copia para evitar modificar original
                
                # Predicción con probabilidades
                pred_class, prob_0, prob_1 = predict_pipeline_proba(data_dict)
                
                # Solo incluir si la predicción es 1 (suscripción positiva)
                if pred_class == 1:
                    results.append({
                        "client_id": client_id,
                        "prediction": pred_class,
                        "probability_class_0": prob_0,
                        "probability_class_1": prob_1,
                        "probability": prob_1,  # alias para acceso directo
                        "timestamp": datetime.now().isoformat(),
                    })
            except (ValueError, RuntimeError) as e:
                # Loguear error para este cliente pero continuar con los otros
                results.append({
                    "client_id": data_dict.get("client_id", idx),
                    "error": str(e),
                    "status": "PREDICTION_ERROR",
                })
            except Exception as e:
                results.append({
                    "client_id": data_dict.get("client_id", idx),
                    "error": str(e),
                    "status": "INTERNAL_ERROR",
                })
        
        # Ordenar por probabilidad descendente
        results_sorted = sorted(
            results, 
            key=lambda x: x.get("probability", 0) if "probability" in x else 0, 
            reverse=True
        )
        
        return {
            "success": True,
            "total_input": len(input_data),
            "total_positive_predictions": len([r for r in results_sorted if "probability" in r]),
            "results": results_sorted,
            "model_version": model_version,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "Error inesperado procesando batch",
            "message": str(e),
            "status": "INTERNAL_ERROR",
            "timestamp": datetime.now().isoformat()
        })