## 📊 Status Brief – Semana 4 (H1)

**Equipo:** BancoXLab  

---

### DoD (Definition of Done)
- Documentación completa en repo: `DATA_DICTIONARY.md`, `reporte_perfil.html`, `baseline.ipynb`, `Perfil_de_datos.py`.  
- Data Readiness Report redactado con fuentes, calidad, profiling y sesgos (HTML adjunto + hallazgos).  
- Baseline naive ejecutado con métrica inicial registrada (accuracy, F1).  
- Evidencia versionada con tag `S4`.  
- Registro de propuestas de decisiones 002, 003, 004 y 005.
---

### Avances desde la última clase
- Se completó el **Data Dictionary** con descripción de todas las columnas y riesgos de sesgo/PII.  
- Se redactó el **Data Readiness Report** con checklist, top-3 problemas y mitigaciones.  
- Se implementó un **baseline naive** como referencia inicial.  
- Se actualizaron los **riesgos (R1–R8)** y se priorizaron los críticos (desbalance, PII, pipeline).  
- Se organizó la arquitectura de alto nivel y 4 ADRs (Batch vs API, Orquestación, etc.) en progreso.  

---

### Riesgos (RAG) + dueño/fecha
- **Dataset desbalanceado (🔴)** – DS  – Mitigación en S5: aplicar SMOTE/class weights.  
- **Conexión pipeline y dependencias (🔴)** – DE/TL – Mitigación en S6: CI/CD + tests de integración.  
- **Sesgos socio-demográficos (🟠)** – DS/PO – Mitigación en S7: fairness metrics y revisión de features.  

---
### Ayuda que necesitamos
- Validación docente sobre el **nivel de detalle suficiente** en el Data Readiness Report (¿falta cuantificación de sesgos o basta con listado cualitativo?).  
- Feedback sobre la **decisión batch vs API** en ADR-0001 (¿es correcto mantener batch diario en MVP?).  
- Recomendaciones sobre métricas de fairness más adecuadas para este dataset.

---

### Links
- **Repo:** [BancoXLab/deteccion_clientes_banco](https://github.com/BancoXLab/deteccion_clientes_banco)  
- **Docs:**  
  - [`docs/reporte_perfil.html`](https://github.com/BancoXLab/deteccion_clientes_banco/blob/main/docs/reporte_perfil.html)  
  - [`docs/Perfil_de_datos.py`](https://github.com/BancoXLab/deteccion_clientes_banco/blob/main/scr/ingesta/Perfil_de_datos.py)  
  - [`models/baseline.ipynb`](https://github.com/BancoXLab/deteccion_clientes_banco/blob/main/models/baseline.ipynb)  
  - [`docs/DATA_DICTIONARY.md`](https://github.com/BancoXLab/deteccion_clientes_banco/blob/main/docs/DATA_DICTIONARY.md)  
