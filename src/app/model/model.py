import pickle
from pathlib import Path
import numpy as np
from typing import Dict, Any
import pandas as pd

__version__ = "0.1.0"

# Ruta del modelo (archivo .pkl dentro de la carpeta model)
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / f"trained_pipeline-{__version__}.pkl"

# Cargar el modelo entrenado. Preferir el modelo en `model/` en la raíz del repo
# (fixture de tests guarda ahí). Si no existe, usar el empaquetado en `src/app/model/`.
import os

# Allow overriding model path via env var for clarity in deploy/tests
env_model = os.getenv("BANCX_MODEL_PATH")
if env_model:
    env_path = Path(env_model)
    if env_path.exists():
        load_path = env_path
    else:
        raise FileNotFoundError(f"BANCX_MODEL_PATH está definido pero no existe: {env_path}")
else:
    alt = Path.cwd() / "model" / f"trained_pipeline-{__version__}.pkl"
    if alt.exists():
        load_path = alt
    elif MODEL_PATH.exists():
        load_path = MODEL_PATH
    else:
        raise FileNotFoundError(f"Modelo no encontrado en {alt} ni en {MODEL_PATH}; define BANCX_MODEL_PATH si usas otra ruta")

with open(load_path, "rb") as f:
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

    # construir X como DataFrame para mantener nombres de columnas (evita warnings de sklearn)
    try:
        X = pd.DataFrame([{col: input_data[col] for col in FEATURE_COLUMNS}])
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


def predict_pipeline_proba(input_data: Dict[str, Any]) -> tuple:
    """
    Predice clase y devuelve probabilidades.
    Retorna: (clase, probabilidad_clase_0, probabilidad_clase_1)
    """
    # comprobar que todas las columnas requeridas estén en input_data
    missing = [c for c in FEATURE_COLUMNS if c not in input_data]
    if missing:
        raise ValueError(f"Faltan columnas en los datos de entrada: {missing}")

    # construir X
    # construir X como DataFrame para mantener nombres de columnas (evita warnings de sklearn)
    try:
        X = pd.DataFrame([{col: input_data[col] for col in FEATURE_COLUMNS}])
    except KeyError as e:
        raise ValueError(f"Falta la columna esperada en los datos de entrada: {e}")
    except Exception as e:
        raise RuntimeError(f"Error construyendo la matriz de entrada: {e}")

    # validar tamaño esperado por el modelo si es posible
    expected = _model_expected_feature_count()
    if expected != -1 and expected != X.shape[1]:
        raise RuntimeError(
            f"El modelo espera {expected} features pero la entrada tiene {X.shape[1]}. "
            "Asegúrate de que la lista FEATURE_COLUMNS coincida con las features usadas al entrenar."
        )

    # predecir clase y probabilidades
    try:
        pred_class = model.predict(X)
        pred_proba = model.predict_proba(X) if hasattr(model, "predict_proba") else None
        
        if pred_proba is None:
            # Si el modelo no tiene predict_proba, devolver probabilidad 1.0 para la clase predicha
            prob_0 = 0.0 if pred_class[0] == 1 else 1.0
            prob_1 = 1.0 if pred_class[0] == 1 else 0.0
            return int(pred_class[0]), prob_0, prob_1
        
        # predict_proba devuelve [prob_clase_0, prob_clase_1]
        return int(pred_class[0]), float(pred_proba[0][0]), float(pred_proba[0][1])
    except Exception as e:
        raise RuntimeError(f"Error durante la predicción: {e}")
