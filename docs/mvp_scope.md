# Alcance MVP v1

## Objetivo
Construir un prototipo funcional y reproducible que permita clasificar clientes de BancoX en función de la probabilidad de suscripción a un depósito a plazo.

---

## Historias clave
1. **Como ingeniero de datos**, quiero limpiar y preprocesar el dataset (nulos, duplicados, codificación), **para asegurar que los modelos puedan entrenar sin errores**.  
2. **Como científico de datos**, quiero entrenar un modelo baseline (Regresión Logística), **para obtener una métrica inicial de desempeño**.  
3. **Como científico de datos**, quiero probar un modelo avanzado (Random Forest o Gradient Boosting), **para mejorar la sensibilidad (recall) y precisión**.  
4. **Como ingeniero de datos**, quiero disponer de un pipeline reproducible (`make train` o script único), **para que cualquiera en el equipo pueda ejecutar el entrenamiento de forma consistente**.  
5. **Como product owner**, quiero un reporte de métricas (F1, AUC, PR-AUC, recall) **para poder evaluar si el MVP cumple los KPIs definidos**.  

---

## Criterios de aceptación por historia
1. Dataset limpio con menos del 1% de nulos y sin duplicados → commit en repo con notebook/script de limpieza.  
2. Modelo baseline entrenado (LogReg) con métricas calculadas → archivo `results/baseline_metrics.csv` en repo.  
3. Modelo avanzado entrenado (RF/GBM) con comparación contra baseline → archivo `results/model_comparison.csv`.  
4. Pipeline reproducible documentado en `README.md` que genere métricas con un único comando.  
5. Reporte de métricas exportado (CSV o tabla en README) y revisado en commit etiquetado `S5`.  

---

## 📋 Definition of Done (DoD) del MVP
- **Evidencia visible**: notebooks/scripts, métricas exportadas (`results/metrics.csv`), commit/tag correspondiente.  
- **Reproducibilidad**: un comando (`make train` o `python src/train.py`) que corra el pipeline de datos → modelo → métricas.  
- **Resultado observable**: archivo de métricas y predicciones generado en `/results/`.  
- **Calidad mínima**: pipeline corre en limpio, sin errores, con seed fijado y dependencias en `requirements.txt`.  
- **Documentación**: instrucciones en `README.md` con cómo correr el MVP y supuestos del dataset.

---

## In Scope
- Limpieza y preprocesamiento básico de datos (nulos, duplicados, codificación).
- Entrenamiento de un modelo baseline (Regresión Logística y Random Forest).
- Validación con métricas de clasificación (F1, PR-AUC).
- Script reproducible (`make train` o notebook) que entrene el modelo y genere métricas.

## Out of Scope
- Integración con CRM.
- Despliegue en ambiente productivo.
- Dashboard final con visualización avanzada.
- Monitoreo y reentrenamiento continuo.

## KPIs SMART
- **F1 ≥ 0.72** para el set de validación al 30/09/2025.
- **Freshness ≤ 24h** en dataset de prueba al 30/09/2025.
