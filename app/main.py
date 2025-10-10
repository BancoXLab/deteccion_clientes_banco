from fastapi import FastAPI
from pydantic import BaseModel
from model.model import predict_pipeline, __version__ as model_version

app = FastAPI()

# Columnas de entrada para el modelo
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
    y: int
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

@app.get("/")
def home():
    return {"message": "API is up and running", "model_version": model_version}

@app.post("/predict")
def predict(input_data: ClientData):
    prediction = predict_pipeline(input_data.dict())
    return {
        "prediction": prediction,
        "model_version": model_version,
    }