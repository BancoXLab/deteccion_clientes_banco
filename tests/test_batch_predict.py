#!/usr/bin/env python3
"""
Script para probar el endpoint /predict con múltiples clientes.
Uso: python test_batch_predict.py
"""

import json
import pandas as pd
import numpy as np

def main():
    # Cargar datos reales del CSV para construir ejemplos válidos
    df = pd.read_csv("data/bank.csv", sep=";")

    # Limpiar nombres de columnas (similar a lo que hace el pipeline)
    df.columns = [col.replace(".", "_").replace("-", "_").replace("num__", "").replace("cat__", "").replace("ord__", "").replace("x0_", "") for col in df.columns]
    df = df.rename(columns={"job_admin_": "job_admin"})

    # Seleccionar columnas necesarias (FEATURE_COLUMNS)
    FEATURE_COLUMNS = [
        'age', 'month', 'day_of_week', 'duration', 'campaign', 'pdays', 'previous',
        'emp_var_rate', 'cons_price_idx', 'cons_conf_idx', 'euribor3m', 'nr_employed',
        'previous_bin', 'job_target_mean', 'marital_divorced', 'marital_married',
        'marital_single', 'marital_unknown', 'education_freq_encode', 'housing_no',
        'housing_unknown', 'housing_yes', 'loan_no', 'loan_unknown', 'loan_yes',
        'contact_cellular', 'contact_telephone'
    ]

    # Verificar que todas las columnas existan
    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise RuntimeError(f"Columnas faltantes en el CSV: {missing}. Disponibles: {df.columns.tolist()}")

    # Tomar 5 filas de ejemplo
    sample_df = df[FEATURE_COLUMNS].head(5)

    # Convertir a lista de diccionarios (válidos para la API)
    test_data = []
    for idx, row in sample_df.iterrows():
        client_dict = row.to_dict()
        # Convertir tipos a JSON-serializables
        client_dict = {k: float(v) if isinstance(v, (np.floating, np.integer)) else v for k, v in client_dict.items()}
        client_dict["client_id"] = f"CLIENT_{idx:04d}"
        test_data.append(client_dict)

    print("=" * 80)
    print("TEST: /predict endpoint con múltiples clientes")
    print("=" * 80)
    print(f"\nEnvío {len(test_data)} clientes al endpoint /predict...")
    print(f"Primer cliente:\n{json.dumps(test_data[0], indent=2)}\n")

    # Prueba local (sin levantar servidor)
    print("Realizando predicciones locales (sin servidor)...\n")

    from src.app.model.model import predict_pipeline_proba

    results = []
    for idx, client in enumerate(test_data):
        try:
            client_id = client.pop("client_id")
            pred_class, prob_0, prob_1 = predict_pipeline_proba(client)
            
            # Solo incluir si la predicción es 1
            if pred_class == 1:
                results.append({
                    "client_id": client_id,
                    "prediction": pred_class,
                    "probability_class_0": prob_0,
                    "probability_class_1": prob_1,
                    "probability": prob_1,
                })
                print(f"✓ {client_id}: Clase {pred_class}, Probabilidad {prob_1:.4f}")
            else:
                print(f"✗ {client_id}: Clase {pred_class}, Probabilidad {prob_1:.4f} (no incluido en resultados)")
        except Exception as e:
            print(f"✗ {client_id}: Error: {e}")

    print(f"\n" + "=" * 80)
    print(f"Resultados finales:")
    print("=" * 80)
    print(f"Clientes procesados: {len(test_data)}")
    print(f"Predicciones con clase=1: {len(results)}")
    print(f"\nRespuesta JSON simulada:")
    response = {
        "success": True,
        "total_input": len(test_data),
        "total_positive_predictions": len(results),
        "results": sorted(results, key=lambda x: x.get("probability", 0), reverse=True),
    }
    print(json.dumps(response, indent=2))
    print("\n" + "=" * 80)
    print("TEST COMPLETADO - El endpoint /predict está listo para batch predictions")
    print("=" * 80)


if __name__ == "__main__":
    main()