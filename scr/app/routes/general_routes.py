from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import threading
from datetime import datetime
from prefect import flow, task, get_run_logger
from scr.app.model.model import predict_pipeline, __version__ as model_version
from scr.utils.errors import handle_exceptions

router = APIRouter(tags=["General Endpoints"])

# Modelo de datos
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
