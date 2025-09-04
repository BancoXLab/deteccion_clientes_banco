# 📘 Data Dictionary – Bank Marketing Dataset

**Fuente:** [UCI Machine Learning Repository – Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing)  
**Licencia:** Público, UCI Repository (para fines educativos e investigativos)  
**Dataset utilizado:** `bank-additional-full.csv`  
**Datasets complementarios:** `bank_full.csv`, `bank.csv`
---

## Información general
- **Observaciones:** 41,188 clientes  
- **Variables:** 20 + 1 variable objetivo (`y`)  
- **Unidad de análisis:** cliente contactado en una campaña de marketing  
- **Periodo:** 2008–2013, datos de una institución bancaria portuguesa  

---

## Diccionario de variables

| Campo | Descripción | Tipo | Dominio / Valores posibles | Es PII | Sesgo potencial |
|-------|-------------|------|----------------------------|--------|-----------------|
| `age` | Edad del cliente | int | valores ≥ 18 | No | Sí (edad puede sesgar) |
| `job` | Tipo de trabajo | categórico | admin., services, technician, retired, student, etc. | No | Sí (socioeconómico) |
| `marital` | Estado civil | categórico | casado, soltero, divorciado/viudo | No | Sí (puede generar sesgo) |
| `education` | Nivel educativo | categórico | primaria, secundaria, terciaria, desconocido | No | Sí |
| `default` | ¿Crédito en mora? | binario | sí, no | No | Bajo |
| `housing` | ¿Préstamo de vivienda? | binario | sí, no | No | Bajo |
| `loan` | ¿Préstamo personal? | binario | sí, no | No | Bajo |
| `contact` | Canal de contacto | categórico | teléfono, celular, desconocido | No | No |
| `month` | Último mes de contacto | categórico | ene, feb, mar, …, dic | No | No |
| `day_of_week` | Día de la semana del último contacto | categórico | lun–vie | No | No |
| `duration` | Duración del último contacto (segundos) | int | valores ≥ 0 | No | Alto riesgo de leakage (solo conocido post-contacto) |
| `campaign` | Nº contactos en campaña actual | int | ≥ 1 | No | No |
| `pdays` | Días desde último contacto previo | int | -1 = no contactado | No | No |
| `previous` | Nº de contactos anteriores | int | ≥ 0 | No | No |
| `poutcome` | Resultado campaña anterior | categórico | éxito, fracaso, otro, desconocido | No | No |
| `emp.var.rate` | Tasa variación empleo trimestral | float | continuo | No | No |
| `cons.price.idx` | Índice de precios al consumidor | float | continuo | No | No |
| `cons.conf.idx` | Índice de confianza del consumidor | float | continuo | No | No |
| `euribor3m` | Tasa Euribor 3m | float | continuo | No | No |
| `nr.employed` | Nº empleados a nivel agregado | float | continuo | No | No |
| `y` | **Variable objetivo**: suscripción a depósito | binario | sí, no | No | – |

---

## Notas y hallazgos
- `duration`: **no debe usarse para predicción** porque introduce *data leakage* (sólo se conoce después de llamar al cliente).  
- Variables socio-demográficas (`age`, `job`, `marital`, `education`) → riesgo de sesgo y fairness.  
- Algunas columnas tienen valores "desconocido" que deben tratarse en limpieza.  

---

## Estado de Readiness
- [x] Fuente y licencia documentadas  
- [x] Diccionario de datos creado  
- [x] Profiling automático revisado (HTML adjunto)  
- [ ] Sesgos documentados en mayor profundidad  
- [ ] Split train/val/test definido  
