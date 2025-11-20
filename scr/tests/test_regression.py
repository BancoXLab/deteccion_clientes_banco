import os
import json
import pickle
import pandas as pd
from pathlib import Path
from sklearn.metrics import f1_score

# Config desde env o rutas por defecto
MLFLOW_CSV = Path(os.getenv("MLFLOW_METRICS_CSV", "mlflow_metrics.csv"))
EVAL_DATA = Path(os.getenv("EVAL_DATA_PQ", "data/eval.parquet"))
CANDIDATE_MODEL = Path(os.getenv("CANDIDATE_MODEL_PKL", "model/trained_pipeline-0.1.0.pkl"))

# tolerancia mínima para reemplazo (por ejemplo 0.01 = 1%)
MIN_IMPROVEMENT = float(os.getenv("MIN_IMPROVEMENT", "0.01"))

def load_model(pkl_path: Path):
    with open(pkl_path, "rb") as f:
        return pickle.load(f)

def test_candidate_beats_champion():
    assert MLFLOW_CSV.exists(), f"{MLFLOW_CSV} no existe; configura MLFLOW_METRICS_CSV"
    assert EVAL_DATA.exists(), f"{EVAL_DATA} no existe; configura EVAL_DATA_PQ"
    assert CANDIDATE_MODEL.exists(), f"{CANDIDATE_MODEL} no existe; configura CANDIDATE_MODEL_PKL"

    df_metrics = pd.read_csv(MLFLOW_CSV)
    assert "f1_score" in df_metrics.columns, "mlflow CSV debe contener columna f1_score"
    # champion = fila con mayor f1_score
    champ_row = df_metrics.loc[df_metrics["f1_score"].idxmax()]
    champion_f1 = float(champ_row["f1_score"])

    # cargar dataset de evaluación y separar X,y (ajusta según tu dataset)
    df_eval = pd.read_parquet(EVAL_DATA)
    assert "y" in df_eval.columns, "Dataset de evaluación necesita columna 'y'"
    X_eval = df_eval.drop(columns=["y"])
    y_true = df_eval["y"]

    # cargar candidate model y predecir (asegúrate que pipeline y FEATURE_COLUMNS coinciden)
    model = load_model(CANDIDATE_MODEL)
    y_pred = model.predict(X_eval)
    candidate_f1 = float(f1_score(y_true, y_pred))
    # criterio: candidate debe superar champion por MIN_IMPROVEMENT
    assert candidate_f1 >= champion_f1 + MIN_IMPROVEMENT, (
        f"Candidate f1={candidate_f1:.4f} no supera champion f1={champion_f1:.4f} "
        f"con mejora mínima requerida {MIN_IMPROVEMENT}"
    )