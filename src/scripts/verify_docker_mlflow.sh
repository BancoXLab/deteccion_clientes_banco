#!/bin/bash
# Script para verificar que Docker Compose con MLflow está bien configurado

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         VERIFICACIÓN DE DOCKER COMPOSE + MLFLOW                ║"
echo "╚════════════════════════════════════════════════════════════════╝"

PROJECT_DIR="/workspaces/deteccion_clientes_banco"

# 1. Validar archivo
echo ""
echo "🔍 PASO 1: Validando docker-compose.yml..."
if docker-compose -f "$PROJECT_DIR/docker-compose.yml" config > /dev/null 2>&1; then
    echo "✓ docker-compose.yml es válido"
else
    echo "❌ Error en docker-compose.yml"
    exit 1
fi

# 2. Verificar que MLflow está en el archivo
echo ""
echo "🔍 PASO 2: Verificando servicio MLflow..."
if grep -q "mlflow:" "$PROJECT_DIR/docker-compose.yml"; then
    echo "✓ Servicio MLflow encontrado"
else
    echo "❌ Servicio MLflow NO encontrado"
    exit 1
fi

# 3. Verificar configuración de MLflow
echo ""
echo "🔍 PASO 3: Verificando configuración de MLflow..."
if grep -q "ghcr.io/mlflow/mlflow" "$PROJECT_DIR/docker-compose.yml"; then
    echo "✓ Imagen de MLflow configurada correctamente"
else
    echo "❌ Imagen de MLflow NO configurada"
    exit 1
fi

# 4. Verificar puerto 5000
echo ""
echo "🔍 PASO 4: Verificando puerto 5000..."
if grep -q "5000:5000" "$PROJECT_DIR/docker-compose.yml"; then
    echo "✓ Puerto 5000 expuesto correctamente"
else
    echo "❌ Puerto 5000 NO expuesto"
    exit 1
fi

# 5. Verificar volumen mlflow_data
echo ""
echo "🔍 PASO 5: Verificando volumen MLflow..."
if grep -q "mlflow_data:" "$PROJECT_DIR/docker-compose.yml"; then
    echo "✓ Volumen mlflow_data configurado"
else
    echo "❌ Volumen mlflow_data NO configurado"
    exit 1
fi

# 6. Verificar que fastapi depende de mlflow
echo ""
echo "🔍 PASO 6: Verificando dependencias..."
if grep -A 20 "fastapi:" "$PROJECT_DIR/docker-compose.yml" | grep -q "MLFLOW_TRACKING_URI"; then
    echo "✓ FastAPI configurado para conectar a MLflow"
else
    echo "❌ FastAPI NO configurado para MLflow"
    exit 1
fi

# 7. Verificar training-pipeline
echo ""
echo "🔍 PASO 7: Verificando training-pipeline..."
if grep -A 30 "training-pipeline:" "$PROJECT_DIR/docker-compose.yml" | grep -q "MLFLOW_TRACKING_URI"; then
    echo "✓ Training-pipeline configurado para MLflow"
else
    echo "❌ Training-pipeline NO configurado para MLflow"
    exit 1
fi

# 8. Mostrar resumen
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    VERIFICACIÓN EXITOSA ✅                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "📊 CONFIGURACIÓN:"
echo "  • Servicio MLflow: ✓"
echo "  • Puerto: 5000"
echo "  • Backend: SQLite (/mlflow/mlflow.db)"
echo "  • Artifacts: /mlflow/artifacts"
echo "  • Volumen persistente: mlflow_data"
echo "  • Red: bancox_network"

echo ""
echo "🚀 PRÓXIMOS PASOS:"
echo ""
echo "1. Levantar servicios:"
echo "   $ docker-compose up -d"
echo ""
echo "2. Esperar a que MLflow esté listo (30 segundos):"
echo "   $ sleep 30"
echo ""
echo "3. Acceder a MLflow UI:"
echo "   $ open http://localhost:5000"
echo ""
echo "4. Ejecutar tests:"
echo "   $ python3 tests/test_train_pipeline.py"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
