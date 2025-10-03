import pickle
from pathlib import Path

__version__ = "0.1.0"

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / 'trained_pipeline-0.1.0.pkl', 'rb') as f:
    model = pickle.load(f)

def predict_pipeline(input_data):

    return