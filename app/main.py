from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model.model import predict_pipeline, __version__ as model_version

app = FastAPI(
    title="Banco X API",
    description="API que predice si un cliente se suscribirá o no usando un modelo entrenado",
    version=model_version
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

@app.get("/")
def home():
    return {
        "message": "✅ La API está levantada y corriendo!",
        "model_version": model_version,
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
