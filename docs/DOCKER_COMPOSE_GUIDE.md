# 🐳 Docker Compose - Guía de Reproducibilidad

Este documento describe cómo reproducir la aplicación completa usando Docker Compose.

## 📋 Servicios Disponibles

La aplicación está estructurada en múltiples servicios:

### API & Inference (Siempre activos)
- **fastapi** (puerto 8000) - API principal con Prefect integration
- **client** - Cliente HTTP para consumir la API
- **streamlit-app** (puerto 8501) - UI principal para predicciones

### Monitoring & Alerting
- **monitor** - Monitor de logs y métricas
- **alert-server** (puerto 9000) - Servidor Flask para visualizar alertas
- **dashboard** (puerto 8500) - Dashboard Streamlit para monitoreo

### ETL & Training (Opcional - requiere profile `training`)
- **data-ingestion** - Pipeline de ingesta de datos (ETL)
- **training-pipeline** - Pipeline de entrenamiento de modelos

### Infrastructure
- **mysql** (puerto 3306) - Base de datos MySQL

## 🚀 Cómo Usar

### 1. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores (opcional, hay defaults)
cat .env
```

### 2. Iniciar Stack Completo (API + Monitoring + Streamlit)

```bash
# Iniciar todos los servicios recomendados
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f
```

**Servicios que se inician:**
- API (8000)
- Streamlit App (8501)
- Monitor Dashboard (8500)
- Alert Server (9000)
- MySQL (3306)

### 3. Iniciar con Training Pipeline (Opcional)

```bash
# Incluir servicios de training
docker compose --profile training up -d
```

**Servicios adicionales:**
- data-ingestion - Carga datos a MySQL
- training-pipeline - Entrena modelo

⚠️ **Nota:** Requiere que MySQL esté funcionando y los datos disponibles.

### 4. Verificar Servicios

```bash
# Ver estado de los servicios
docker compose ps

# Verificar health status
docker compose ps --filter health=healthy
```

### 5. Acceder a los Servicios

| Servicio | URL | Descripción |
|----------|-----|-------------|
| API | http://localhost:8000 | FastAPI con documentación interactiva (/docs) |
| Streamlit App | http://localhost:8501 | UI para predicciones (individual/batch) |
| Monitor Dashboard | http://localhost:8500 | Dashboard de monitoreo del modelo |
| Alert Server | http://localhost:9000 | Servidor de alertas (visualizar en /alerts) |
| MySQL | localhost:3306 | Base de datos (usuario: bancox_user) |

### 6. Probar Predicción desde API

```bash
# Predicción individual
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35, "month": 5, "day_of_week": 1, "duration": 500,
    "campaign": 1, "pdays": -1, "previous": 0, "emp_var_rate": 1.1,
    "cons_price_idx": 93.5, "cons_conf_idx": -36.0, "euribor3m": 0.7,
    "nr_employed": 5100.0, "previous_bin": 0, "job_target_mean": 0.45,
    "marital_divorced": 0, "marital_married": 1, "marital_single": 0,
    "marital_unknown": 0, "education_freq_encode": 0.5, "housing_no": 0,
    "housing_unknown": 0, "housing_yes": 1, "loan_no": 0,
    "loan_unknown": 0, "loan_yes": 1, "contact_cellular": 1, "contact_telephone": 0
  }'
```

### 7. Ver Logs

```bash
# Todos los servicios
docker compose logs

# Servicio específico
docker compose logs fastapi
docker compose logs streamlit-app
docker compose logs training-pipeline

# Últimas 50 líneas
docker compose logs -f --tail=50
```

### 8. Detener Servicios

```bash
# Detener (sin eliminar volúmenes)
docker compose down

# Detener y eliminar volúmenes (limpia la DB)
docker compose down -v

# Detener servicio específico
docker compose stop fastapi
```

## 🔧 Configuración Avanzada

### Personalizar Variables de Entorno

Edita `.env`:

```env
MYSQL_ROOT_PASSWORD=mi_password_segura
MYSQL_USER=mi_usuario
MYSQL_PASSWORD=mi_password
MYSQL_DATABASE=mi_base_datos
```

### Cambiar Puertos

```yaml
# En docker-compose.yml, modifica los ports:
services:
  fastapi:
    ports:
      - "8001:8000"  # Accesible en localhost:8001
```

### Agregar Servicios Adicionales

Edita `docker-compose.yml` y agrega en la sección `services:`:

```yaml
  mi-servicio:
    build: .
    container_name: bancox_mi_servicio
    command: ["/app/venv/bin/python", "/app/src/mi_servicio.py"]
    environment:
      - PYTHONPATH=/app
    networks:
      - bancox_network
```

## 📊 Arquitectura de Servicios

```
┌─────────────────────────────────────────────┐
│         USUARIOS/CLIENTES                   │
└────────────┬────────────────────────────────┘
             │
    ┌────────┴─────────┬──────────────┐
    │                  │              │
    ▼                  ▼              ▼
[API:8000]     [Streamlit:8501] [Monitor:8500]
    │                  │              │
    │                  │              │
    ├──────────────────┼──────────────┤
    │                  │              │
    ▼                  ▼              ▼
┌─────────────────────────────────────────────┐
│        PROCESSING LAYER                     │
│  • Model Predictions (FastAPI)              │
│  • Alert Generation (monitor.py)            │
└────────────┬─────────────────┬──────────────┘
             │                 │
    ┌────────▼──────┐   ┌──────▼─────────┐
    │  Alert Server │   │   MySQL DB     │
    │  (Flask:9000) │   │   (Port:3306)  │
    └───────────────┘   └────────────────┘
```

## 🧪 Testing

### Ejecutar Tests Locales

```bash
# Tests unitarios
pytest tests/ -v

# Tests de integración (requiere servicios activos)
docker compose up -d
pytest tests/ -v -m integration
docker compose down
```

### Ejecutar CI Pipeline Localmente

```bash
# Simular CI.yml
docker compose up -d --build
# Ejecutar health checks y pruebas
curl http://localhost:8000/healthz
docker compose down -v
```

## ⚠️ Troubleshooting

### "Connection refused" en http://localhost:8000

```bash
# Verificar si el servicio está activo
docker compose ps fastapi

# Ver logs del servicio
docker compose logs fastapi

# Esperar a que se inicie
sleep 10 && curl http://localhost:8000/healthz
```

### MySQL no se conecta

```bash
# Verificar si MySQL está listo
docker compose logs mysql

# Comprobar credenciales en .env
cat .env | grep MYSQL

# Reconectar servicios
docker compose restart
```

### Volumen de datos persistente

```bash
# Ver volúmenes
docker volume ls | grep bancox

# Limpiar volúmenes (CUIDADO - elimina datos)
docker compose down -v
```

## 📝 Notas Importantes

1. **Primera ejecución:** MySQL puede tardar 30 segundos en estar listo. Los servicios esperan el health check.

2. **Persistencia:** Los datos de MySQL se guardan en el volumen `mysql_data` (sobreviven a `docker compose down`).

3. **Training Pipeline:** Requiere que los datos estén en MySQL. Ejecuta primero `data-ingestion`:
   ```bash
   docker compose --profile training up data-ingestion
   # Esperar a que termine
   docker compose --profile training up training-pipeline
   ```

4. **Logs:** Los servicios escriben logs en:
   - `/tmp/app.log` (API)
   - `scr/ops/alerts.log` (Alertas)
   - Prefect tracking en `mlruns/`

## 🔗 Recursos Adicionales

- [FastAPI Documentation](http://localhost:8000/docs)
- [Docker Compose Reference](https://docs.docker.com/compose/reference/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
