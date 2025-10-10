import pickle
from pathlib import Path
import numpy as np

__version__ = "0.1.0"
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar el modelo entrenado
BASE_DIR = Path(__file__).resolve().parent
with open(BASE_DIR / 'trained_pipeline-0.1.0.pkl', 'rb') as f:
    model = pickle.load(f)

def predict_pipeline(input_data):
    columns = [
        'age', 'month', 'day_of_week', 'duration', 'campaign', 'pdays', 'previous',
        'emp_var_rate', 'cons_price_idx', 'cons_conf_idx', 'euribor3m', 'nr_employed',
        'y', 'previous_bin', 'job_target_mean', 'marital_divorced', 'marital_married',
        'marital_single', 'marital_unknown', 'education_freq_encode', 'housing_no',
        'housing_unknown', 'housing_yes', 'loan_no', 'loan_unknown', 'loan_yes',
        'contact_cellular', 'contact_telephone'
    ]
    X = np.array([input_data[col] for col in columns]).reshape(1, -1)
    pred = model.predict(X)
    return int(pred[0])