# Plan de Experimentación

## Objetivo
Definir una estrategia clara y ordenada para probar diferentes enfoques de modelado sobre el dataset, evaluando la predicción de los clientes y registrando resultados de forma reproducible.  

---

## Hipótesis iniciales
1. Calidad de datos: si limpiamos valores nulos y atípicos, las métricas mejorarán.  
2. Selección de variables: ciertas columnas tienen más poder predictivo que otras.  
3. Modelos simples: una regresión logística puede alcanzar un baseline aceptable.  
4. Modelos más complejos: árboles de decisión y ensambles pueden superar al baseline.  

---

## Variables de interés
- Variables independientes: [especificar columnas relevantes según dataset, ej. edad, ingresos, educación].  
- Variable objetivo: [columna target, ej. cliente/no cliente].  
- Métricas: Accuracy, F1-score y AUC.  

---

## Protocolo de experimentos
1. Baseline  
   - Modelo: Regresión logística simple.  
   - Datos: versión cruda + split 70/15/15.  
   - Métricas esperadas: >50% Accuracy como línea base.  

2. Preprocesamiento  
   - Imputar nulos (media/moda).  
   - Escalar variables numéricas.  
   - One-hot encoding en variables categóricas.  
   - Comparar métricas antes/después.  

3. Modelos alternativos  
   - Árbol de decisión.  
   - Random Forest.  
   - Gradient Boosting.  
   - Comparar performance vs baseline.  

4. Análisis de errores  
   - Revisar segmentos donde el modelo falla más.  
   - Documentar al menos 3 hallazgos.  

---

## Registro de resultados
- Guardar métricas en `results/metrics.csv`.  
- Capturas o screenshots en `results/screenshots/`.  
- Documentar cada experimento en `experiments/expXX_nombre.md` con:  
  - Objetivo.  
  - Configuración.  
  - Resultados.  
  - Conclusión breve.  

---

## Criterios de éxito
- Baseline reproducible con un solo comando.  
- Al menos un modelo que supere el baseline en F1-score.  
- Registro ordenado y versionado de los experimentos.  

---

Este plan no es rígido: los equipos pueden agregar más experimentos según el tiempo y los resultados que vayan obteniendo.  
