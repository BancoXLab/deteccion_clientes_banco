#!/usr/bin/env python3
"""
Ejemplo de uso del pipeline de entrenamiento integrado.
Demuestra cómo ejecutar y monitorear el training.
"""

import sys
sys.path.insert(0, "/workspaces/deteccion_clientes_banco")

# Ejemplo 1: Entrenar con modelo XGBoost
def example_train_xgboost():
    """Entrenar con XGBoost (modelo por defecto)."""
    print("\n" + "="*70)
    print("EJEMPLO 1: Entrenamiento con XGBoost")
    print("="*70)
    
    from src.training.train_pipeline import train_pipeline
    
    print("\nEjecutando pipeline...")
    # train_pipeline()  # Descomentar para ejecutar
    print("✓ Pipeline completado (comentado - descomentar para ejecutar)")


# Ejemplo 2: Entrenar con Random Forest
def example_train_random_forest():
    """Entrenar con Random Forest."""
    print("\n" + "="*70)
    print("EJEMPLO 2: Entrenamiento con Random Forest")
    print("="*70)
    
    from src.training.train_pipeline import train_pipeline
    
    print("\nEjecutando pipeline con Random Forest...")
    # train_pipeline(model_type="Random Forest")  # Descomentar para ejecutar
    print("✓ Pipeline completado (comentado - descomentar para ejecutar)")


# Ejemplo 3: Entrenar con Logistic Regression
def example_train_logistic_regression():
    """Entrenar con Logistic Regression."""
    print("\n" + "="*70)
    print("EJEMPLO 3: Entrenamiento con Logistic Regression")
    print("="*70)
    
    from src.training.train_pipeline import train_pipeline
    
    print("\nEjecutando pipeline con Logistic Regression...")
    # train_pipeline(model_type="Logistic Regression")  # Descomentar para ejecutar
    print("✓ Pipeline completado (comentado - descomentar para ejecutar)")


# Ejemplo 4: Monitorear resultados
def example_monitor_results():
    """Monitorear y analizar resultados del entrenamiento."""
    print("\n" + "="*70)
    print("EJEMPLO 4: Monitoreo de Resultados")
    print("="*70)
    
    import pandas as pd
    from pathlib import Path
    import json
    
    results_dir = Path("/workspaces/deteccion_clientes_banco/artifacts/resultados")
    model_dir = Path("/workspaces/deteccion_clientes_banco/model")
    
    # Leer CSV de métricas
    metrics_file = results_dir / "training_metrics.csv"
    if metrics_file.exists():
        df = pd.read_csv(metrics_file)
        print("\n📊 HISTORIAL DE ENTRENAMIENTOS:")
        print(df[["timestamp", "modelo", "f1", "f1_improvement", "should_deploy"]].to_string())
    else:
        print("\n⚠ No hay histórico de entrenamientos aún")
    
    # Leer metadatos del modelo
    metadata_file = model_dir / "model_metadata.txt"
    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        print("\n🏆 MODELO EN PRODUCCIÓN:")
        print(f"  - Tipo: {metadata['model_type']}")
        print(f"  - F1 Score: {metadata['f1_score']:.4f}")
        print(f"  - Accuracy: {metadata['accuracy']:.4f}")
        print(f"  - Recall: {metadata['recall']:.4f}")
        print(f"  - Precision: {metadata['precision']:.4f}")
        print(f"  - ROC-AUC: {metadata['roc_auc']:.4f}")
        print(f"  - Timestamp: {metadata['timestamp']}")
    else:
        print("\n⚠ No hay modelo en producción aún")


# Ejemplo 5: Comparación entre modelos
def example_compare_models():
    """Comparar desempeño entre diferentes modelos."""
    print("\n" + "="*70)
    print("EJEMPLO 5: Comparación de Modelos")
    print("="*70)
    
    import pandas as pd
    from pathlib import Path
    
    metrics_file = Path("/workspaces/deteccion_clientes_banco/artifacts/resultados/training_metrics.csv")
    
    if metrics_file.exists():
        df = pd.read_csv(metrics_file)
        
        # Agrupar por modelo
        comparison = df.groupby("modelo")[["accuracy", "recall", "precision", "f1", "roc_auc"]].mean()
        
        print("\n📈 COMPARACIÓN DE MODELOS (Promedio):")
        print(comparison.round(4))
        
        # Mejor modelo por F1
        best_f1 = df.loc[df["f1"].idxmax()]
        print(f"\n🏅 Mejor F1 Score:")
        print(f"  - Modelo: {best_f1['modelo']}")
        print(f"  - F1: {best_f1['f1']:.4f}")
        print(f"  - Fecha: {best_f1['timestamp']}")
    else:
        print("\n⚠ No hay datos de comparación aún")


# Ejemplo 6: Simular entrenamiento sin Prefect
def example_train_without_prefect():
    """Entrenar directamente sin usar Prefect (útil para debugging)."""
    print("\n" + "="*70)
    print("EJEMPLO 6: Entrenamiento Directo (sin Prefect)")
    print("="*70)
    
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from pathlib import Path
    
    from src.training.train_pipeline import (
        _train_model,
        _calculate_metrics,
        _load_production_model_f1
    )
    
    try:
        # Cargar datos
        data_path = "/workspaces/deteccion_clientes_banco/data/df_resampled.csv"
        if not Path(data_path).exists():
            print(f"❌ Datos no encontrados: {data_path}")
            return
        
        df = pd.read_csv(data_path)
        print(f"✓ Datos cargados: {df.shape}")
        
        # Split train/test
        train, test = train_test_split(df, test_size=0.2, random_state=42)
        X_train = train.drop("y", axis=1)
        Y_train = train["y"]
        X_test = test.drop("y", axis=1)
        Y_test = test["y"]
        
        # Entrenar modelo
        model_type = "XGBoost"
        print(f"\nEntrenando {model_type}...")
        model, params, y_pred, y_prob = _train_model(
            model_type, X_train, Y_train, X_test
        )
        y_pred_train = model.predict(X_train)
        
        # Calcular métricas
        metrics = _calculate_metrics(Y_test, y_pred, y_prob, Y_train, y_pred_train)
        
        # Comparar con producción
        f1_production = _load_production_model_f1()
        f1_improvement = metrics["f1"] - f1_production
        
        print(f"\n✅ Resultados:")
        print(f"  - F1 Score: {metrics['f1']:.4f}")
        print(f"  - Accuracy: {metrics['accuracy']:.4f}")
        print(f"  - Recall: {metrics['recall']:.4f}")
        print(f"  - Precision: {metrics['precision']:.4f}")
        print(f"  - ROC-AUC: {metrics['roc_auc']:.4f}")
        print(f"\n  - F1 Producción: {f1_production:.4f}")
        print(f"  - Mejora: {f1_improvement:+.4f}")
        
        if f1_improvement > 0:
            print(f"  - Decisión: ✅ DESPLEGAR")
        else:
            print(f"  - Decisión: ⚠ MANTENER ACTUAL")
    
    except Exception as e:
        print(f"❌ Error: {e}")


# Ejemplo 7: Ver estructura de directorios
def example_project_structure():
    """Mostrar estructura de directorios generada."""
    print("\n" + "="*70)
    print("EJEMPLO 7: Estructura de Directorios")
    print("="*70)
    
    from pathlib import Path
    
    print("\n📁 Ubicaciones Importantes:")
    
    locations = {
        "Pipeline": "/workspaces/deteccion_clientes_banco/src/training/train_pipeline.py",
        "Tests": "/workspaces/deteccion_clientes_banco/tests/test_train_pipeline.py",
        "Datos": "/workspaces/deteccion_clientes_banco/data/df_resampled.csv",
        "Modelo (Producción)": "/workspaces/deteccion_clientes_banco/model/trained_pipeline-0.1.0.pkl",
        "Metadatos": "/workspaces/deteccion_clientes_banco/model/model_metadata.txt",
        "CSV Métricas": "/workspaces/deteccion_clientes_banco/artifacts/resultados/training_metrics.csv",
        "Documentación": "/workspaces/deteccion_clientes_banco/docs/TRAIN_PIPELINE_GUIDE.md",
    }
    
    for name, path in locations.items():
        exists = "✓" if Path(path).exists() else "○"
        print(f"  {exists} {name}")
        print(f"     └─ {path}")
    
    print("\n📊 MLflow Tracking:")
    print(f"  └─ http://0.0.0.0:5000")


# Ejemplo 8: Instrucciones de inicio
def example_quickstart():
    """Instrucciones rápidas para comenzar."""
    print("\n" + "="*70)
    print("EJEMPLO 8: Guía Rápida de Inicio")
    print("="*70)
    
    instructions = """
🚀 PASOS PARA COMENZAR:

1️⃣  Instalar dependencias:
    pip install -r requirements.txt

2️⃣  Configurar variables de entorno:
    cp .env.example .env  (si existe)
    # Editar .env con tus credenciales de MySQL

3️⃣  Iniciar MLflow (en terminal separada):
    mlflow ui --host 0.0.0.0 --port 5000

4️⃣  Validar instalación:
    python tests/test_train_pipeline.py

5️⃣  Ejecutar pipeline (primera ejecución):
    python -c "from src.training.train_pipeline import train_pipeline; train_pipeline()"

6️⃣  Monitorear resultados:
    - MLflow: http://0.0.0.0:5000
    - CSV: artifacts/resultados/training_metrics.csv
    - Modelo: model/trained_pipeline-0.1.0.pkl

📖 DOCUMENTACIÓN:
    - docs/TRAIN_PIPELINE_GUIDE.md (detallada)
    - INTEGRATION_SUMMARY.md (resumen de cambios)

💡 TIPS:
    - Primera ejecución: F1 = 0 → Siempre despliega
    - Revisar logs de Prefect para debugging
    - MLflow guarda todos los runs históricos
    - Backups de modelo están en model/model_backup_*.pkl
"""
    print(instructions)


def main():
    """Ejecutor principal."""
    print("\n" + "#"*70)
    print("# EJEMPLOS DE USO - PIPELINE DE ENTRENAMIENTO")
    print("#"*70)
    
    examples = {
        "1": ("Entrenar con XGBoost", example_train_xgboost),
        "2": ("Entrenar con Random Forest", example_train_random_forest),
        "3": ("Entrenar con Logistic Regression", example_train_logistic_regression),
        "4": ("Monitorear Resultados", example_monitor_results),
        "5": ("Comparar Modelos", example_compare_models),
        "6": ("Entrenamiento Directo", example_train_without_prefect),
        "7": ("Estructura de Directorios", example_project_structure),
        "8": ("Guía Rápida", example_quickstart),
        "0": ("Ejecutar Todos", None),
    }
    
    print("\nEjemplos disponibles:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelecciona un ejemplo (0-8) [default=8]: ").strip() or "8"
    
    if choice == "0":
        for i in range(1, 9):
            examples[str(i)][1]()
    elif choice in examples and examples[choice][1]:
        examples[choice][1]()
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    main()
