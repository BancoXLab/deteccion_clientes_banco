# script: retrain_model.py
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import pickle

# Determinar raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Cargar datos
print("Cargando datos...")
data_path = PROJECT_ROOT / "data" / "bank.csv"
if not data_path.exists():
    print(f"❌ No encontrado: {data_path}")
    exit(1)

df = pd.read_csv(data_path)
print(f"✓ Datos: {df.shape}")

# Preprocesamiento
X = df.drop('y', axis=1)
y = df['y'].map({'yes': 1, 'no': 0})

# Seleccionar features requeridas
from src.app.model.model import FEATURE_COLUMNS
X = X[FEATURE_COLUMNS]

print(f"Class distribution ANTES SMOTE: {y.value_counts().to_dict()}")

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# SMOTE
smote = SMOTE(sampling_strategy={1: len(y_train[y_train==0])}, k_neighbors=5, random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

print(f"Class distribution DESPUÉS SMOTE: {pd.Series(y_train_smote).value_counts().to_dict()}")

# Crear pipeline MEJORADO
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(
        n_estimators=200,        # ← Aumentado de 10 a 200
        max_depth=10,            # ← Limitado para regularización
        min_samples_leaf=5,      # ← Aumentado para evitar overfitting
        random_state=42,
        n_jobs=-1               # ← Usar todos los cores
    ))
])

# Entrenar
print("\nEntrenando modelo...")
pipeline.fit(X_train_smote, y_train_smote)

# Evaluar
from sklearn.metrics import f1_score, recall_score, precision_score, roc_auc_score
y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)[:, 1]

print(f"\n📊 Resultados en Test Set:")
print(f"  F1-Score: {f1_score(y_test, y_pred):.4f}")
print(f"  Recall: {recall_score(y_test, y_pred):.4f}")
print(f"  Precision: {precision_score(y_test, y_pred):.4f}")
print(f"  ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")

# Guardar
model_path = PROJECT_ROOT / "model" / "trained_pipeline-0.1.0.pkl"
model_path.parent.mkdir(parents=True, exist_ok=True)
with open(model_path, "wb") as f:
    pickle.dump(pipeline, f)

print(f"\n✓ Modelo guardado en {model_path}")
print(f"✓ Reinicia la API para cargar el nuevo modelo")
