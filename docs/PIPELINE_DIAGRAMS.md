# Diagrama del Pipeline de Entrenamiento

## Flujo General

```
┌──────────────────────────────────────────────────────────────────────┐
│                      PIPELINE DE ENTRENAMIENTO                       │
│                     (src/training/train_pipeline.py)                 │
└──────────────────────────────────────────────────────────────────────┘

                              ⬇️  INICIO

                     ┌──────────────────────┐
                     │   load_data()        │
                     │  Cargar MySQL        │
                     │  → dataset_raw.pq    │
                     └──────────┬───────────┘
                                ⬇️
                     ┌──────────────────────┐
                     │   apply_smote()      │
                     │  Oversampling        │
                     │  → dataset_resampled │
                     └──────────┬───────────┘
                                ⬇️
                ┌───────────────────────────────────────┐
                │  save_transformed_data()              │
                │  Guardar en MySQL_prepared_data       │
                └───────────────────┬───────────────────┘
                                    ⬇️
                ┌────────────────────────────────────────────────────┐
                │  train_classification_model()                      │
                │  ┌──────────────────────────────────────────────┐  │
                │  │ 1. Split train/test (80/20)                  │  │
                │  │    X_train, Y_train, X_test, Y_test          │  │
                │  ├──────────────────────────────────────────────┤  │
                │  │ 2. Elegir modelo:                            │  │
                │  │    - XGBoost (default)                       │  │
                │  │    - Random Forest                           │  │
                │  │    - Logistic Regression                     │  │
                │  ├──────────────────────────────────────────────┤  │
                │  │ 3. Entrenar: model.fit(X_train, Y_train)    │  │
                │  ├──────────────────────────────────────────────┤  │
                │  │ 4. Predicciones: y_pred, y_prob              │  │
                │  ├──────────────────────────────────────────────┤  │
                │  │ 5. Calcular métricas:                        │  │
                │  │    - accuracy, precision, recall, f1         │  │
                │  │    - roc_auc, accuracy_train                 │  │
                │  ├──────────────────────────────────────────────┤  │
                │  │ 6. Obtener F1 modelo producción              │  │
                │  │    f1_production = _load_production_model()  │  │
                │  ├──────────────────────────────────────────────┤  │
                │  │ 7. Calcular mejora:                          │  │
                │  │    f1_improvement = f1_new - f1_production   │  │
                │  │    should_deploy = (f1_improvement > 0)      │  │
                │  ├──────────────────────────────────────────────┤  │
                │  │ 8. Registrar en MLflow:                      │  │
                │  │    - Parámetros del modelo                   │  │
                │  │    - Todas las métricas                      │  │
                │  │    - Modelo entrenado                        │  │
                │  ├──────────────────────────────────────────────┤  │
                │  │ 9. Guardar registro en CSV:                  │  │
                │  │    artifacts/resultados/training_metrics.csv │  │
                │  └──────────────────────────────────────────────┘  │
                └───────────────────┬────────────────────────────────┘
                                    ⬇️
              ┌─────────────────────────────────────────────┐
              │     ¿Mejora de F1 Score?                   │
              │     (f1_improvement > 0)                   │
              └──────┬──────────────────────────┬──────────┘
                     │YES                      │NO
                    ⬇️                          ⬇️
         ┌──────────────────────┐    ┌─────────────────────┐
         │save_model_if_improved│    │ Mantener modelo     │
         │ ✅ DESPLEGAR        │    │ actual en producción│
         │                      │    └─────────────────────┘
         │ 1. Hacer backup      │
         │ 2. Guardar nuevo PKL │
         │ 3. Actualizar JSON   │
         └──────────┬───────────┘
                    ⬇️
         ┌──────────────────────┐
         │  clean_temp_files()  │
         │  Limpiar parquets    │
         └──────────┬───────────┘
                    ⬇️
              ⬅️  FIN EXITOSO  ✅

```

---

## Decisión de Despliegue

```
                   🔍 LÓGICA DE DESPLIEGUE

        ┌─────────────────────────────────────┐
        │   F1_nuevo > F1_producción?         │
        └────┬────────────────────────────┬───┘
             │ SÍ                         │ NO
             ⬇️                           ⬇️
    ┌──────────────────────┐    ┌──────────────────────┐
    │ ✅ DESPLEGAR NUEVO   │    │ ⚠️  MANTENER ACTUAL  │
    │                      │    │                      │
    │ Guardar como:        │    │ Registrar log:       │
    │ - PKL en producción  │    │ - should_deploy=False
    │ - Backup con fecha   │    │ - f1_improvement<0   │
    │ - Metadatos JSON     │    │                      │
    │ - Registro en CSV    │    │ No modifica:         │
    │                      │    │ - Modelo vigente     │
    │ Log: "✅ Modelo      │    │ - CSV histórico      │
    │  actualizado"        │    │ - Backups anterior   │
    └──────────────────────┘    └──────────────────────┘
```

---

## Entrada / Salida de Datos

```
                         📥 ENTRADA
                            │
                    ┌───────┴────────┐
                    │                │
            ┌───────────────────┐  ┌──────────────────┐
            │  MySQL Database   │  │  .env variables  │
            │                   │  │                  │
            │ - table: BancoX   │  │ - DB credentials │
            │ - 36k+ records    │  │ - Paths          │
            │ - 27+ features    │  │ - MLflow URI     │
            └────────┬──────────┘  └──────────────────┘
                     │
                     └─────────── train_pipeline() ──────────────┐
                                                                 │
                                  ⬇️
                    ┌───────────────────────────────────┐
                    │  Procesamiento y Entrenamiento    │
                    │  (ver diagrama anterior)          │
                    └───────────────┬───────────────────┘
                                    ⬇️
                              📤 SALIDA
            ┌──────────────────────────────────────────────────────┐
            │                                                      │
    ┌───────────────┐  ┌──────────────────┐  ┌────────────────┐   │
    │ 📊 MLflow     │  │ 📁 model/ dir    │  │ 📈 CSV metrics │   │
    │               │  │                  │  │                │   │
    │ Experimento:  │  │ - .pkl (model)   │  │ - training_    │   │
    │ BancoX-       │  │ - .txt (metadata)│  │   metrics.csv  │   │
    │ {model_type}  │  │ - *_backup.pkl   │  │                │   │
    │               │  │                  │  │ Columnas:      │   │
    │ Cada Run:     │  │ JSON Metadata:   │  │ - timestamp    │   │
    │ - Params      │  │ {                │  │ - modelo       │   │
    │ - Metrics     │  │   timestamp,     │  │ - metrics      │   │
    │ - Model       │  │   model_type,    │  │ - f1_improvement
    │ - Artifacts   │  │   f1_score,      │  │ - should_deploy
    │               │  │   accuracy, ...  │  │                │   │
    │ URI:          │  │ }                │  │ Histórico:     │   │
    │ http://0.0.0  │  │                  │  │ Acumulativo    │   │
    │ .0:5000       │  │ Backup:          │  │ Append mode    │   │
    │               │  │ model_backup_    │  │                │   │
    │               │  │ YYYYMMDD_HHMMSS  │  │                │   │
    └───────────────┘  └──────────────────┘  └────────────────┘   │
            │                  │                     │              │
            └──────────────────┴─────────────────────┘              │
                                                                    │
            Actualización en Producción:                           │
            Si f1_improvement > 0:                                 │
                → Guardar model en trained_pipeline-0.1.0.pkl     │
                → Crear backup del anterior                        │
                → Actualizar metadata.txt                          │
            Si f1_improvement <= 0:                                │
                → Mantener modelo vigente                          │
                → Solo registro en CSV                             │
                                                                    │
            └────────────────────────────────────────────────────┘
```

---

## Métricas Calculadas

```
                    📊 MÉTRICAS REGISTRADAS

┌─────────────────────────────────────────────────────────────┐
│                   DESEMPEÑO DEL MODELO                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ accuracy     = (TP + TN) / Total                           │
│              └─→ Exactitud general                         │
│                                                             │
│ precision    = TP / (TP + FP)                              │
│              └─→ De nuestras predicciones positivas,       │
│                   ¿cuántas fueron correctas?               │
│                                                             │
│ recall       = TP / (TP + FN)                              │
│              └─→ De los positivos reales,                  │
│                   ¿cuántos encontramos?                    │
│                                                             │
│ f1_score     = 2 × (precision × recall) / (precision + recall)
│              └─→ Media armónica (balance P-R)    🎯        │
│                                                             │
│ roc_auc      = Área bajo la curva ROC                      │
│              └─→ Capacidad discriminativa                  │
│                   [0=malo, 1=perfecto]                     │
│                                                             │
│ accuracy_train = Accuracy en conjunto de entrenamiento    │
│                └─→ Detectar overfitting                   │
│                   Si >> accuracy_test → Overfitting       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

                    🎯 MÉTRICA DE DECISIÓN

┌─────────────────────────────────────────────────────────────┐
│                        F1 SCORE                             │
│                                                             │
│ Es el principal indicador para decidir despliegue           │
│                                                             │
│ ✅ Si F1_nuevo > F1_producción                             │
│    → Modelo mejoró, desplegar                              │
│                                                             │
│ ⚠️  Si F1_nuevo ≤ F1_producción                            │
│    → Modelo no mejoró, mantener actual                     │
│                                                             │
│ 📝 Se registra en CSV:                                     │
│    f1_improvement = F1_nuevo - F1_producción               │
│    should_deploy = (f1_improvement > 0)                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Ciclo de Vida Completo

```
                    ♻️ CICLO DE VIDA

    Tiempo →

    [DÍA 1] First Run
    ├─ Entrenar modelo
    ├─ F1_producción = 0 (no existe)
    ├─ F1_nuevo = 0.8232
    └─ ✅ Desplegar (primera vez)
        └─ model_metadata.txt: {f1: 0.8232, ...}
        └─ training_metrics.csv: {f1: 0.8232, should_deploy: True}

    [DÍA 2] Second Run
    ├─ Entrenar modelo (nuevos datos)
    ├─ F1_producción = 0.8232 (del día anterior)
    ├─ F1_nuevo = 0.8350
    ├─ Mejora = +0.0118 ✓
    └─ ✅ Desplegar (mejoró)
        └─ model_backup_20250120_143022.pkl (backup anterior)
        └─ model_metadata.txt: {f1: 0.8350, ...}
        └─ training_metrics.csv: {f1: 0.8350, should_deploy: True}

    [DÍA 3] Third Run
    ├─ Entrenar modelo
    ├─ F1_producción = 0.8350 (del día anterior)
    ├─ F1_nuevo = 0.8200
    ├─ Mejora = -0.0150 ✗
    └─ ⚠️  Mantener (no mejoró)
        └─ model_backup_20250121_030000.pkl (sin cambios)
        └─ model_metadata.txt: {f1: 0.8350, ...} (sin cambios)
        └─ training_metrics.csv: {f1: 0.8200, should_deploy: False} (+ registro)

    [DÍA 4] Fourth Run
    ├─ Entrenar modelo
    ├─ F1_producción = 0.8350 (seguido del día 2)
    ├─ F1_nuevo = 0.8500
    ├─ Mejora = +0.0150 ✓
    └─ ✅ Desplegar (mejoró)
        └─ model_backup_20250122_030000.pkl (backup anterior)
        └─ model_metadata.txt: {f1: 0.8500, ...}
        └─ training_metrics.csv: {f1: 0.8500, should_deploy: True} (+ registro)

    HISTORIAL ACUMULADO EN CSV:
    ┌──────────┬────────┬──────┬──────────────┬──────────────┐
    │timestamp │modelo  │  f1  │f1_improvement│should_deploy │
    ├──────────┼────────┼──────┼──────────────┼──────────────┤
    │2025-01-20│XGBoost │0.8232│    +0.8232   │     True     │
    │2025-01-21│XGBoost │0.8350│    +0.0118   │     True     │
    │2025-01-22│XGBoost │0.8200│    -0.0150   │     False    │
    │2025-01-23│XGBoost │0.8500│    +0.0150   │     True     │
    └──────────┴────────┴──────┴──────────────┴──────────────┘
```

---

## Integración con MLflow

```
                 🔗 MLFLOW TRACKING

    Experimento: BancoX-{model_type}
    (e.g., BancoX-XGBoost, BancoX-Random Forest)

    Cada Run:
    ┌──────────────────────────────────────┐
    │ Run Name: {model}_{YYYYMMDD_HHMMSS}  │
    │                                      │
    │ PARAMETERS:                          │
    │ ├─ n_estimators: 100                 │
    │ ├─ learning_rate: 0.1                │
    │ ├─ max_depth: 6                      │
    │ └─ ... (según modelo)                │
    │                                      │
    │ METRICS:                             │
    │ ├─ accuracy: 0.9123                  │
    │ ├─ precision: 0.8200                 │
    │ ├─ recall: 0.8500                    │
    │ ├─ f1: 0.8232                        │
    │ ├─ roc_auc: 0.9500                   │
    │ ├─ accuracy_train: 0.9456            │
    │ ├─ f1_production: 0.8000             │
    │ ├─ f1_improvement: 0.0232            │
    │ └─ should_deploy: true               │
    │                                      │
    │ MODEL:                               │
    │ ├─ Format: XGBoost / Sklearn         │
    │ ├─ Type: Classification              │
    │ └─ Size: ~50MB (típico)              │
    │                                      │
    │ ARTIFACTS:                           │
    │ └─ data_info.txt                     │
    │    ├─ Train samples: 37238           │
    │    └─ Test samples: 9310             │
    │                                      │
    └──────────────────────────────────────┘

    Acceso: http://0.0.0.0:5000
    ├─ Ver experimentos
    ├─ Comparar runs
    ├─ Descargar modelos
    └─ Visualizar métricas
```
