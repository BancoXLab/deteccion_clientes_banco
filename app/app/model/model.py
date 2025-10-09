import pickle
import numpy as np
import pandas as pd
from pathlib import Path

__version__ = "0.1.0"

BASE_DIR = Path(__file__).resolve().parent

# Cargar modelo
model_path = BASE_DIR / "trained_pipeline-0.1.0.pkl"

with open(model_path, "rb") as f:
    model = pickle.load(f)

# Pipeline de predicción
def predict_pipeline(input_data: dict):
    """
    input_data: dict con las columnas requeridas.
    """
    # Convertimos a DataFrame (1 fila)
    data = pd.DataFrame([input_data])

    # Realizamos predicción
    prediction = model.predict(data)

    # Retornar resultado
    return prediction[0]
