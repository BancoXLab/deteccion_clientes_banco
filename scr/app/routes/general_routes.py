from fastapi import APIRouter, HTTPException
from scr.app.schemas import ClientData
import pandas as pd
import threading
from datetime import datetime
from prefect import flow, task, get_run_logger
from scr.app.model.model import predict_pipeline, predict_pipeline_proba, __version__ as model_version
from scr.utils.errors import handle_exceptions

router = APIRouter(tags=["General Endpoints"])

# Usar el modelo central `ClientData` desde `scr.app.schemas` para evitar duplicados

# Prefect 
@task
def log_prediction_to_prefect(input_data: dict, prediction: float):
    logger = get_run_logger()
    logger.info("Registrando inferencia en Prefect...")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info(f"Modelo: {model_version}")
    logger.info(f"Predicción: {prediction}")
    logger.info(f"Input: {input_data}")
    logger.info("Registro completado.")



@flow(name="Flow de inferencia Banco X")
def inference_flow(input_data: dict, prediction: float):
    log_prediction_to_prefect(input_data, prediction)

# Endpoints
@router.get("/ping")
@handle_exceptions(reraise=True)
def ping():
    return {"ping": "pong"}

@router.post("/predict/single")
@handle_exceptions(reraise=True)
def predict(input_data: ClientData):
    try:
        # Usar model_dump para compatibilidad con Pydantic v2
        input_dict = input_data.model_dump()

        # Obtener clase y probabilidades
        pred_class, prob_0, prob_1 = predict_pipeline_proba(input_dict)
        prediction = float(pred_class)

        # Loguear en background
        threading.Thread(target=inference_flow, args=(input_dict, prediction)).start()

        return {
            "prediction": prediction,
            "probability_class_0": prob_0,
            "probability_class_1": prob_1,
            "model_version": model_version,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": "Invalid input", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
