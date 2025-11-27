#!/usr/bin/env python3
"""
Script de prueba para validar la integración del pipeline de entrenamiento.
Permite probar cada componente de manera independiente.
"""

import os
import sys
import pandas as pd
import pickle
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Agregar ruta del proyecto
sys.path.insert(0, "/workspaces/deteccion_clientes_banco")

from src.training.train_pipeline import (
    _train_model,
    _calculate_metrics,
    _load_production_model_f1,
    MODEL_DIR,
    RESULTS_DIR
)

def test_model_training():
    """Prueba el entrenamiento de modelos sin Prefect."""
    print("\n" + "="*60)
    print("TEST 1: Entrenamiento de Modelos")
    print("="*60)
    
    # Cargar datos de prueba
    data_path = "/workspaces/deteccion_clientes_banco/data/df_resampled.csv"
    if not Path(data_path).exists():
        print(f"❌ Archivo de datos no encontrado: {data_path}")
        return False
    
    df = pd.read_csv(data_path)
    print(f"✓ Datos cargados: {df.shape}")
    
    # Split train/test
    from sklearn.model_selection import train_test_split
    train, test = train_test_split(df, test_size=0.2, random_state=42)
    
    X_train = train.drop("y", axis=1)
    Y_train = train["y"]
    X_test = test.drop("y", axis=1)
    Y_test = test["y"]
    
    print(f"✓ Train shape: {X_train.shape}, Test shape: {X_test.shape}")
    
    # Probar cada modelo
    models = ["XGBoost", "Random Forest", "Logistic Regression"]
    results = {}
    
    for model_type in models:
        print(f"\n  Entrenando {model_type}...", end=" ")
        try:
            model, params, y_pred, y_prob = _train_model(
                model_type, X_train, Y_train, X_test
            )
            y_pred_train = model.predict(X_train)
            metrics = _calculate_metrics(Y_test, y_pred, y_prob, Y_train, y_pred_train)
            results[model_type] = metrics
            print(f"✓ F1: {metrics['f1']:.4f}")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print(f"\n✓ Todos los modelos entrenados correctamente")
    return True


def test_production_model_loading():
    """Prueba la carga del modelo en producción."""
    print("\n" + "="*60)
    print("TEST 2: Carga del Modelo en Producción")
    print("="*60)
    
    try:
        f1_production = _load_production_model_f1()
        print(f"✓ F1 score en producción: {f1_production:.4f}")
        
        if f1_production == 0.0:
            print("  ⚠ No hay modelo en producción aún (será la primera ejecución)")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_directories():
    """Prueba que los directorios necesarios existen."""
    print("\n" + "="*60)
    print("TEST 3: Directorios y Permisos")
    print("="*60)
    
    dirs_to_check = [
        (MODEL_DIR, "Modelos"),
        (RESULTS_DIR, "Resultados"),
    ]
    
    all_ok = True
    for dir_path, name in dirs_to_check:
        exists = dir_path.exists()
        readable = os.access(dir_path, os.R_OK) if exists else False
        writable = os.access(dir_path, os.W_OK) if exists else False
        
        status = "✓" if (exists and readable and writable) else "❌"
        print(f"{status} {name}: {dir_path}")
        
        if not (exists and readable and writable):
            all_ok = False
    
    return all_ok


def test_mlflow_connection():
    """Prueba la conexión con MLflow."""
    print("\n" + "="*60)
    print("TEST 4: Conexión con MLflow")
    print("="*60)
    
    try:
        import mlflow
        tracking_uri = mlflow.get_tracking_uri()
        print(f"✓ MLflow tracking URI: {tracking_uri}")
        
        # Intentar crear un experimento
        mlflow.set_experiment("test-pipeline")
        print(f"✓ Experimento de prueba creado")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_metrics_file():
    """Prueba la escritura del archivo de métricas."""
    print("\n" + "="*60)
    print("TEST 5: Archivo de Métricas")
    print("="*60)
    
    try:
        metrics_file = RESULTS_DIR / "training_metrics.csv"
        
        # Crear archivo de prueba
        test_record = pd.DataFrame([{
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modelo": "TEST",
            "accuracy": 0.9123,
            "recall": 0.8500,
            "precision": 0.8200,
            "f1": 0.8350,
            "accuracy_train": 0.9456,
            "roc_auc": 0.9500,
            "f1_production": 0.8000,
            "f1_improvement": 0.0350,
            "should_deploy": True
        }])
        
        if metrics_file.exists():
            test_record.to_csv(metrics_file, mode="a", header=False, index=False)
            print(f"✓ Registro añadido a archivo existente")
        else:
            test_record.to_csv(metrics_file, index=False)
            print(f"✓ Archivo de métricas creado")
        
        # Verificar
        df = pd.read_csv(metrics_file)
        print(f"✓ Archivo contiene {len(df)} registros")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Ejecuta todos los tests."""
    print("\n" + "#"*60)
    print("# VALIDACIÓN DEL PIPELINE DE ENTRENAMIENTO")
    print("#"*60)
    
    tests = [
        ("Directorios", test_directories),
        ("Conexión MLflow", test_mlflow_connection),
        ("Entrenamiento de Modelos", test_model_training),
        ("Carga de Modelo en Producción", test_production_model_loading),
        ("Archivo de Métricas", test_metrics_file),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Error inesperado en {test_name}: {e}")
            results[test_name] = False
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE TESTS")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResultado: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n✅ ¡Pipeline listo para usar!")
        return True
    else:
        print(f"\n⚠ {total - passed} test(s) fallido(s). Revisa los errores arriba.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
