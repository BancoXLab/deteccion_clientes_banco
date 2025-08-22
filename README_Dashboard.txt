Proyecto: Seguimiento de modelo de clasificación de clientes para campañas de depósitos.

----------------------------------------------------------------------

Requisitos

Python 3.8 o superior

Paquetes necesarios:

pip install streamlit pandas plotly

----------------------------------------------------------------------

Estructura esperada del proyecto

C:...\Detección_clientes_de_banco\models
├── app.py                         ← Script del dashboard
├── metrics.csv                   ← Métricas del modelo
├── clientes_segmentados.csv     ← Datos cliente por cliente
├── predicciones.csv             ← Predicciones con probabilidades
├── roc_curve.csv                ← Curva ROC
├── pr_curve.csv                 ← Curva Precision-Recall
├── impact.csv                   ← ROI antes y después del modelo
├── training_status.csv          ← Estado del entrenamiento
Asegúrese de que todos los archivos CSV estén en la misma carpeta que app.py.

----------------------------------------------------------------------

Instrucciones para ejecutar el dashboard
Abre una terminal en la carpeta del proyecto.

Ejecuta los siguientes comandos:

cd path (ruta de carpeta hacia\Detección_clientes_de_banco\models)

streamlit run dashboard_seguimiento.py

El navegador abrirá automáticamente el dashboard en:


http://localhost:8501

----------------------------------------------------------------------------

¿Qué se puede visualizar?
Métricas del modelo (Precision, Recall, ROC AUC)

Predicciones por cliente y probabilidades

Curva ROC y Precision-Recall

Análisis por segmento (edad, trabajo, etc.)

Impacto en la campaña (ROI estimado)

Estado del entrenamiento y drift

Filtro por umbral de aceptación

--------------------------------------------------------------------------

Contacto
En caso de dudas o problemas, contactar al equipo responsable del proyecto o revisar los comentarios dentro del notebook MVP+Dashboard.ipynb.