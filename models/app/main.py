from fastapi import FastAPI
from pydantic import BaseModel
from app.model.model import predict_pipeline
from app.model.model import __version__ as model_version

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is up and running", "model_version": model_version}

@app.post("/predict")
def predict(input_data: BaseModel):
    prediction = predict_pipeline(input_data.dict())
    return {"prediction": prediction, "model_version": model_version}