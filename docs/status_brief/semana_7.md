## Status Brief – Semana 7

**Equipo:** BancoXLab  

**Objetivo de esta clase (1 entrega concreta):**  
- Entregar una solución concreta: automatización de la comparación y despliegue de modelos en MLflow, asegurando que el mejor modelo se promueva a producción de forma controlada y documentada.

---
### DoD (Definition of Done)
- Implementación y registro de nuevos modelos en MLflow, con comparación automática contra el modelo en producción.
- Notebook actualizado para comparar métricas y promover el mejor modelo a producción.
- Documentación de la lógica de comparación y despliegue en el repo.
- Evidencia versionada con tag S7.
- Actualización de reporte de riesgos y mitigaciones.

---
### Avances desde la última clase
- Se automatizó la comparación de métricas entre el modelo actual en producción y el nuevo modelo entrenado.
- Se implementó la lógica para registrar y promover automáticamente el mejor modelo en MLflow.
- Se corrigió el Makefile para ejecutar notebooks y guardar salidas correctamente.
- Se documentó el proceso de actualización de modelos en producción.
- Se revisaron y actualizaron los riesgos críticos del pipeline y fairness.

---
### Riesgos (RAG) + dueño/fecha


---
### Ayuda que necesitamos
- Validación docente sobre la lógica de comparación y despliegue automático en MLflow.
- Feedback sobre la robustez del pipeline de actualización de modelos.
- Recomendaciones sobre métricas adicionales para fairness y monitoreo.

### Links
- [`models/baseline.ipynb`](https://github.com/BancoXLab/deteccion_clientes_banco/blob/main/models/baseline.ipynb)  
- [`Makefile (comando reproducible)`](https://github.com/BancoXLab/deteccion_clientes_banco/blob/main/Makefile)
- 