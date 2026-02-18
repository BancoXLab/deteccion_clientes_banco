# script: train_xgboost_model.py
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import pickle

# Determinar raíz del proyecto (dos niveles arriba: src/training -> project root)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Cargar datos
print("Cargando datos...")
data_path = PROJECT_ROOT / "data" / "bank.csv"
# Leer CSV crudo primero
raw = pd.read_csv(data_path)

# Normalizar nombres de columnas: reemplazar puntos por guiones bajos y limpiar espacios
raw.columns = [c.strip().replace('.', '_') for c in raw.columns]

from src.app.model.model import FEATURE_COLUMNS

# Si el CSV crudo no contiene las features esperadas, intentar usar el dataset preprocesado
if set(FEATURE_COLUMNS).issubset(set(raw.columns)):
    df_used = raw
else:
    alt_path = PROJECT_ROOT / "data" / "df_resampled.csv"
    if alt_path.exists():
        alt = pd.read_csv(alt_path)
        alt.columns = [c.strip().replace('.', '_') for c in alt.columns]
        if set(FEATURE_COLUMNS).issubset(set(alt.columns)):
            df_used = alt
        else:
            missing = [c for c in FEATURE_COLUMNS if c not in alt.columns]
            raise KeyError(f"Faltan columnas en el dataset preprocesado: {missing}. Ejecuta el pipeline de preprocesamiento antes de entrenar.")
    else:
        missing = [c for c in FEATURE_COLUMNS if c not in raw.columns]
        raise KeyError(f"Columnas esperadas no encontradas en {data_path}: {missing}. Usa el dataset preprocesado (data/df_resampled.csv) o ejecuta el pipeline de preparación.")

# Separar X/y usando el dataset seleccionado
X = df_used.drop('y', axis=1)
# Manejar posibles formatos de la columna 'y' (strings 'yes'/'no' o 0/1 numérico)
y_raw = df_used['y']
if y_raw.dtype == object:
    y = y_raw.map({'yes': 1, 'no': 0})
else:
    y = y_raw.astype(int)

# Verificar que no queden NaNs en y
if y.isna().any():
    missing_count = int(y.isna().sum())
    raise ValueError(f"La columna target 'y' contiene {missing_count} valores NaN. Revisar el dataset preprocesado.")

# Asegurarse de que las columnas estén en el orden esperado
X = X[FEATURE_COLUMNS]

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# SMOTE
smote = SMOTE(k_neighbors=5, random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

# Pipeline con XGBoost
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=sum(y_train_smote == 0) / sum(y_train_smote == 1),  # Balance automático
        objective='binary:logistic',
        random_state=42,
        n_jobs=-1,
        verbose=0
    ))
])

print("\nEntrenando XGBoost...")
pipeline.fit(X_train_smote, y_train_smote)

# Guardar
model_path = PROJECT_ROOT / "model" / "trained_pipeline-0.1.0.pkl"
model_path.parent.mkdir(parents=True, exist_ok=True)
with open(model_path, "wb") as f:
    pickle.dump(pipeline, f)

print(f"\n✓ Modelo XGBoost guardado en {model_path}")
