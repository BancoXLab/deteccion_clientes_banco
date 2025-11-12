from fastapi import APIRouter, HTTPException
from scr.app.schemas import ClientData
import pandas as pd
import threading
from datetime import datetime
from prefect import flow, task, get_run_logger
from scr.app.model.model import predict_pipeline, __version__ as model_version
from scr.utils.errors import handle_exceptions

router = APIRouter(tags=["General Endpoints"])

# Modelo de datos: importado desde scr.app.schemas.ClientData

# Prefect 
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
    log_prediction_to_prefect(input_data, prediction)

# Endpoints
@router.get("/ping")
@handle_exceptions(reraise=True)
def ping():
    return {"ping": "pong"}

@router.post("/predict")
@handle_exceptions(reraise=True)
def predict(input_data: ClientData):
    try:
        input_dict = input_data.dict()
        input_df = pd.DataFrame([input_dict])
        prediction = predict_pipeline(input_df)
        prediction = float(prediction)

        threading.Thread(target=inference_flow, args=(input_dict, prediction)).start()

        return {"prediction": prediction, "model_version": model_version}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
