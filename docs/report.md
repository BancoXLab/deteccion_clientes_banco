# 📊 Data Readiness Report – Bank Marketing Dataset

**Equipo:** BancoXLab  
**Fecha:** Semana 4 (S4)  
**Fuente de datos:** [UCI ML Repo – Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing)  
**Licencia:** Uso académico / investigativo (UCI)  
**Archivo base:** `bank-additional-full.csv` (41,188 registros, 20 variables + target)
**Archivos complementarios:** `bank_full.csv`, `bank.csv`
---

## 1. Origen y licencias
Los datos provienen de una institución bancaria portuguesa y fueron publicados en el UCI ML Repository. Se pueden usar con fines educativos e investigativos.  

---

## 2. Diccionario de datos
El detalle columna por columna se encuentra en [`DATA_DICTIONARY.md`](deteccion_clientes_banco/docs/DATA_DICTIONARY.md).  

---

## 3. Calidad de datos
**Hallazgos del profiling (HTML adjunto en `deteccion_clientes_banco/docs/reporte_perfil.html`):**
- Nulos: algunas columnas tienen valores "unknown" que representan ≈5–10% de registros.  
- Duplicados: no se detectaron registros duplicados exactos.  
- Outliers: variables numéricas (`age`, `duration`) presentan valores extremos.  
- Leakage: la variable `duration` no debe usarse en el entrenamiento.  

**Top 3 problemas y mitigación:**
1. `unknown` en variables categóricas → imputación o categoría separada.  
2. Outliers en `age` y `duration` → winsorization o recorte.  
3. `duration` → excluir del set de features predictivas.  

---

## 4. Profiling
Se generó un reporte automático (HTML) con métricas básicas: distribuciones, correlaciones, cardinalidad y outliers.  
📎 Archivo: `deteccion_clientes_banco/docs/reporte_perfil.html`  

---

## 5. Sesgos y privacidad
- Variables sensibles: `age`, `job`, `marital`, `education` → riesgo de sesgo socioeconómico.  
- PII: no contiene datos de identificación personal (nombres, direcciones).  
- Mitigación: métricas de fairness y exclusión de variables si se detecta discriminación.  

---

## 6. Particiones (train/val/test)
Se propone:  
- **Train:** 70%  
- **Validación:** 15%  
- **Test:** 15%  
Split estratificado por variable objetivo `y` para mantener balance de clases.  
Posible validación temporal si se confirma orden temporal en los datos.  

---

## 7. Riesgos de datos (Top-3)
| Riesgo | Prob. | Impacto | Mitigación |
|--------|-------|---------|------------|
| Desbalance de clases (11% positivos) | A | A | Rebalanceo (SMOTE, class weights) |
| Sesgo por variables socio-demográficas | M | A | Métricas de fairness, exclusión si aplica |
| Leakage por `duration` | A | A | Excluir del entrenamiento |

---

## Checklist Data Readiness
- [x] Fuente y licencia documentadas  
- [x] Diccionario de datos en repo  
- [x] Profiling inicial (HTML)  
- [x] Problemas de calidad identificados  
- [ ] Sesgos cuantificados (pendiente)  
- [ ] Particiones aplicadas en código (pendiente)  

---

**DoD (Definition of Done):**
- Documento `data_readiness_report.md` creado y versionado.  
- `DATA_DICTIONARY.md` vinculado.  
- Profiling HTML disponible en `/results/`.  
- Top-3 riesgos de datos identificados con mitigación.  
