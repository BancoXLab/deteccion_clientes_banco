import pickle
from pathlib import Path
import numpy as np
from typing import Dict, Any

__version__ = "0.1.0"

# Ruta del modelo (archivo .pkl dentro de la carpeta model)
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / f"trained_pipeline-{__version__}.pkl"

# Cargar el modelo entrenado
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# Lista de columnas/orden que espera el modelo (sin la variable target 'y')
FEATURE_COLUMNS = [
    'age', 'month', 'day_of_week', 'duration', 'campaign', 'pdays', 'previous',
    'emp_var_rate', 'cons_price_idx', 'cons_conf_idx', 'euribor3m', 'nr_employed',
    'previous_bin', 'job_target_mean', 'marital_divorced', 'marital_married',
    'marital_single', 'marital_unknown', 'education_freq_encode', 'housing_no',
    'housing_unknown', 'housing_yes', 'loan_no', 'loan_unknown', 'loan_yes',
    'contact_cellular', 'contact_telephone'
]


def _model_expected_feature_count() -> int:
    try:
        if hasattr(model, "n_features_in_"):
            return int(getattr(model, "n_features_in_"))
        if hasattr(model, "feature_names_in_"):
            return len(getattr(model, "feature_names_in_"))
    except Exception:
        pass
    return -1


def predict_pipeline(input_data: Dict[str, Any]) -> int:
    # comprobar que todas las columnas requeridas estén en input_data
    missing = [c for c in FEATURE_COLUMNS if c not in input_data]
    if missing:
        raise ValueError(f"Faltan columnas en los datos de entrada: {missing}")

    # construir X
    try:
        X = np.array([input_data[col] for col in FEATURE_COLUMNS]).reshape(1, -1)
    except KeyError as e:
        raise ValueError(f"Falta la columna esperada en los datos de entrada: {e}")
    except Exception as e:
        raise RuntimeError(f"Error construyendo la matriz de entrada: {e}")

    # validar tamaño esperado por el modelo si es posible
    expected = _model_expected_feature_count()
    if expected != -1 and expected != X.shape[1]:
        # Mensaje claro para saber qué hacer
        raise RuntimeError(
            f"El modelo espera {expected} features pero la entrada tiene {X.shape[1]}. "
            "Asegúrate de que la lista FEATURE_COLUMNS coincide con las features usadas "
            "al entrenar el modelo. Si el modelo fue entrenado incluyendo la columna target 'y', "
            "debes reentrenarlo sin la target en las features."
        )

    # predecir
    try:
        pred = model.predict(X)
        return int(pred[0])
    except Exception as e:
        raise RuntimeError(f"Error durante la predicción: {e}")
