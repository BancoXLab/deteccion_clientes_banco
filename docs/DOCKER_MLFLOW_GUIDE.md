# 🐳 Docker Compose - MLflow Integration

## ¿Qué se hizo?

Se integró un servicio de **MLflow** al `docker-compose.yml` que:

✅ Se levanta automáticamente con los demás servicios  
✅ Expone la UI en http://localhost:5000  
✅ Almacena datos en volumen persistente (`mlflow_data`)  
✅ Se conecta automáticamente al pipeline de entrenamiento  
✅ Tiene healthcheck para validar que está listo

---

## 🚀 Cómo Levantar los Servicios

### Opción 1: Stack Completo (Recomendado)

```bash
cd /workspaces/deteccion_clientes_banco

# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver estado de servicios
docker-compose ps
```

### Opción 2: Solo MLflow (Para Tests)

```bash
docker-compose up -d mlflow

# Verificar que está listo
docker-compose logs mlflow

# Acceder a la UI
# http://localhost:5000
```

### Opción 3: Con Pipeline de Entrenamiento

```bash
# Activar profile "training"
docker-compose --profile training up -d

# Ver servicios levantados
docker-compose --profile training ps
```

---

## 📊 Servicios Disponibles

| Servicio | Puerto | Descripción |
|----------|--------|------------|
| **mlflow** | 5000 | MLflow Tracking Server |
| **mysql** | 3306 | Base de datos MySQL |
| **fastapi** | 8000 | API REST |
| **streamlit-app** | 8501 | Dashboard Streamlit |
| **dashboard** | 8500 | Monitor Dashboard |
| **alert-server** | 9000 | Alert Server |

---

## 🧪 Test MLflow Connection

Una vez que los servicios estén levantados, ejecutar el test:

```bash
# Terminal 1: Verificar que MLflow está disponible
curl http://localhost:5000/

# Terminal 2: Ejecutar test del pipeline
python3 tests/test_train_pipeline.py
```

**Resultado esperado:**
```
✓ PASS: Directorios
✓ PASS: Entrenamiento de Modelos
✓ PASS: Carga de Modelo en Producción
✓ PASS: Archivo de Métricas
✓ PASS: Conexión MLflow ✅ (ahora funciona!)
```

---

## 📁 MLflow UI

### Acceso
```
http://localhost:5000
```

### Navegación
1. **Experimentos** - Ver todos los experimentos (`BancoX-XGBoost`, etc.)
2. **Runs** - Cada entrenamiento es un run
3. **Parámetros** - Configuración del modelo
4. **Métricas** - accuracy, precision, recall, f1, roc_auc
5. **Artifacts** - Modelos guardados
6. **Modelos** - Descargar modelos

---

## 🔄 Ciclo Completo

```bash
# 1. Levantar servicios
docker-compose up -d

# 2. Esperar a que esté listo (30-60 segundos)
sleep 60

# 3. Verificar MLflow
curl http://localhost:5000/

# 4. Ejecutar test
python3 tests/test_train_pipeline.py

# 5. Ejecutar pipeline (si MySQL está lista)
python3 -c "from src.training.train_pipeline import train_pipeline; train_pipeline()"

# 6. Ver resultados en MLflow UI
# Abrir: http://localhost:5000
```

---

## 📝 Logs

### Ver todos los logs
```bash
docker-compose logs -f
```

### Ver logs de un servicio específico
```bash
docker-compose logs -f mlflow
docker-compose logs -f training-pipeline
docker-compose logs -f fastapi
```

### Ver últimas 50 líneas
```bash
docker-compose logs --tail=50
```

---

## 🛑 Parar Servicios

### Parar todos
```bash
docker-compose down
```

### Parar todo y limpiar volúmenes
```bash
docker-compose down -v
```

### Parar un servicio específico
```bash
docker-compose stop mlflow
```

---

## 🔧 Configuración de MLflow

### Variables de Entorno en docker-compose.yml

```yaml
mlflow:
  environment:
    - MLFLOW_BACKEND_STORE_URI=sqlite:////mlflow/mlflow.db
    - MLFLOW_DEFAULT_ARTIFACT_ROOT=/mlflow/artifacts
```

### Ubicaciones

- **Backend DB**: `/mlflow/mlflow.db` (dentro del contenedor)
- **Artifacts**: `/mlflow/artifacts` (dentro del contenedor)
- **Volumen**: `mlflow_data` (en el host)

---

## 💾 Persistencia de Datos

MLflow usa un volumen Docker (`mlflow_data`) para persistencia:

```bash
# Ver volúmenes
docker volume ls | grep mlflow

# Inspeccionar volumen
docker volume inspect deteccion_clientes_banco_mlflow_data
```

Los datos persisten incluso si detienes los contenedores:

```bash
docker-compose down  # Parar
# ... cambios, commits, etc ...
docker-compose up -d # Los datos están intactos
```

---

## 🌐 Red de Contenedores

Todos los servicios están en la misma red (`bancox_network`):

```yaml
networks:
  bancox_network:
    driver: bridge
```

Esto permite que los contenedores se comuniquen por nombre:
- `mlflow:5000` desde otros contenedores
- `mysql:3306` desde otros contenedores
- `fastapi:8000` desde otros contenedores

---

## ✅ Verificación Rápida

```bash
# Verificar que MLflow está listo
docker-compose exec mlflow curl http://localhost:5000/ || echo "No listo"

# Ver todas las imágenes
docker images | grep mlflow

# Ver todos los volúmenes
docker volume ls | grep mlflow

# Ver estado detallado
docker-compose ps -a
```

---

## 🚨 Troubleshooting

### MLflow no inicia
```bash
docker-compose logs mlflow
# Verificar puerto 5000 no esté en uso
lsof -i :5000
```

### Error de conexión desde Python
```python
# Verificar URI
os.environ['MLFLOW_TRACKING_URI']  # Debe ser http://mlflow:5000
```

### Volumen no persiste
```bash
# Verificar volumen está montado
docker inspect bancox_mlflow | grep -A 10 Mounts
```

---

## 📊 Integración con Pipeline

El pipeline está configurado para:

1. **Conectar a MLflow automáticamente**
   ```
   MLFLOW_TRACKING_URI=http://mlflow:5000
   ```

2. **Guardar modelos en volumen compartido**
   ```
   BANCX_MODEL_DIR=/app/model
   BANCX_RESULTS_DIR=/app/artifacts/resultados
   ```

3. **Esperar a que MLflow esté listo**
   ```yaml
   depends_on:
     mlflow:
       condition: service_healthy
   ```

---

## 🎯 Próximos Pasos

1. **Levantar servicios**
   ```bash
   docker-compose up -d
   ```

2. **Esperar a que MLflow esté listo**
   ```bash
   docker-compose exec mlflow curl http://localhost:5000/
   ```

3. **Ejecutar test**
   ```bash
   python3 tests/test_train_pipeline.py
   ```

4. **Ver resultados**
   - MLflow UI: http://localhost:5000
   - Logs: `docker-compose logs -f`

---

## 📚 Documentación

- **Docker Compose Docs**: https://docs.docker.com/compose/
- **MLflow Docs**: https://mlflow.org/docs/latest/
- **MLflow Docker**: https://github.com/mlflow/mlflow/pkgs/container/mlflow

---

**Creado por:** GitHub Copilot  
**Fecha:** Noviembre 20, 2025  
**Versión:** 1.0.0 🐳
