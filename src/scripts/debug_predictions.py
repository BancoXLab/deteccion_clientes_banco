#!/usr/bin/env python3
"""
🔍 Script de Debugging para Predicciones de Clase Positiva (ubicado en src/scripts)
"""
import sys
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Any, Tuple

# Determinar raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

def print_header(text):
    print(f"\n{'='*70}\n{text}\n{'='*70}")

def test_model_loading() -> Tuple[bool, Any]:
    print_header("TEST 1: Verificar Carga del Modelo")
    model_paths = [
        PROJECT_ROOT / "model" / "trained_pipeline-0.1.0.pkl",
        Path("./model/trained_pipeline-0.1.0.pkl"),
    ]
    for path in model_paths:
        if path.exists():
            try:
                with open(path, "rb") as f:
                    model = pickle.load(f)
                print("✓ Modelo cargado desde:", path)
                return True, model
            except Exception as e:
                print("Error cargando modelo:", e)
                return False, None
    print("❌ Modelo no encontrado en rutas esperadas")
    return False, None

def test_model_proba_support(model: Any) -> bool:
    print_header("TEST 2: Verificar Soporte de predict_proba")
    if not hasattr(model, 'predict_proba'):
        print("❌ Modelo NO tiene método predict_proba")
        return False
    print("✓ Modelo tiene método predict_proba")
    return True

def get_test_data():
    return {
        'age': 35.0,
        'month': 5,
        'day_of_week': 2,
        'duration': 1200.0,
        'campaign': 5.0,
        'pdays': 999.0,
        'previous': 5.0,
        'emp_var_rate': -1.8,
        'cons_price_idx': 92.893,
        'cons_conf_idx': -46.2,
        'euribor3m': 1.266,
        'nr_employed': 5099.1,
        'previous_bin': 1,
        'job_target_mean': 0.50,
        'marital_divorced': 0,
        'marital_married': 1,
        'marital_single': 0,
        'marital_unknown': 0,
        'education_freq_encode': 0.75,
        'housing_no': 0,
        'housing_unknown': 0,
        'housing_yes': 1,
        'loan_no': 1,
        'loan_unknown': 0,
        'loan_yes': 0,
        'contact_cellular': 1,
        'contact_telephone': 0
    }

def main():
    print_header("🔍 DEBUGGING: Predicciones de Casos Positivos")
    ok, model = test_model_loading()
    if not ok:
        sys.exit(1)
    test_model_proba_support(model)
    from src.app.model.model import FEATURE_COLUMNS
    test_data = get_test_data()
    X = pd.DataFrame([{col: test_data[col] for col in FEATURE_COLUMNS}])
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    print(f"Clase predicha: {pred}")
    print(f"Probabilidades: {proba}")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error:', e)
        raise
