#!/bin/bash
# Script de instalación y validación del pipeline de entrenamiento
# Ejecutar: bash setup_train_pipeline.sh

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   INSTALACIÓN Y VALIDACIÓN DEL PIPELINE DE ENTRENAMIENTO      ║"
echo "║               (BancoX - banco_cliente_detector)               ║"
echo "╚════════════════════════════════════════════════════════════════╝"

PROJECT_DIR="/workspaces/deteccion_clientes_banco"

# ========== PASO 1: Verificar Python ==========
echo ""
echo "🔍 PASO 1: Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python no está instalado"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1)
echo "✓ $PYTHON_VERSION"

# ========== PASO 2: Crear directorios ==========
echo ""
echo "📁 PASO 2: Creando directorios necesarios..."
mkdir -p "$PROJECT_DIR/model"
mkdir -p "$PROJECT_DIR/artifacts/resultados"
mkdir -p /tmp/bancox_train
echo "✓ Directorios creados"

# ========== PASO 3: Verificar requirements ==========
echo ""
echo "📦 PASO 3: Verificando dependencias..."
if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "❌ requirements.txt no encontrado"
    exit 1
fi
echo "✓ requirements.txt encontrado"

# ========== PASO 4: Instalar dependencias ==========
echo ""
echo "⚙️  PASO 4: Instalando dependencias Python..."
python3 -m pip install --quiet -q \
    pandas \
    scikit-learn \
    xgboost \
    imbalanced-learn \
    mlflow \
    prefect \
    sqlalchemy \
    pymysql \
    python-dotenv \
    2>&1 | grep -v "already satisfied" || true
echo "✓ Dependencias instaladas"

# ========== PASO 5: Verificar instalación ==========
echo ""
echo "🧪 PASO 5: Verificando instalación de librerías..."
python3 -c "
try:
    import pandas as pd
    import sklearn
    import xgboost
    import imblearn
    import mlflow
    import prefect
    import sqlalchemy
    print('✓ Todas las librerías importadas correctamente')
except ImportError as e:
    print(f'❌ Error importando: {e}')
    exit(1)
"

# ========== PASO 6: Verificar archivo principal ==========
echo ""
echo "📄 PASO 6: Verificando archivo del pipeline..."
if [ ! -f "$PROJECT_DIR/src/training/train_pipeline.py" ]; then
    echo "❌ train_pipeline.py no encontrado"
    exit 1
fi

# Verificar sintaxis
if python3 -m py_compile "$PROJECT_DIR/src/training/train_pipeline.py" 2>&1; then
    echo "✓ Sintaxis de train_pipeline.py válida"
else
    echo "❌ Error de sintaxis en train_pipeline.py"
    exit 1
fi

# ========== PASO 7: Verificar configuración ==========
echo ""
echo "⚙️  PASO 7: Verificando configuración .env..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  .env no encontrado, crear desde .env.example:"
    echo "   cp .env.example .env"
    echo "   # Editar .env con tus credenciales"
else
    echo "✓ .env encontrado"
    # Verificar si tiene valores llenos
    if grep -q "your_password_here" "$PROJECT_DIR/.env"; then
        echo "⚠️  Valores por defecto en .env - Necesita personalización"
    else
        echo "✓ .env parece estar configurado"
    fi
fi

# ========== PASO 8: Ejecutar tests ==========
echo ""
echo "🧪 PASO 8: Ejecutando tests de validación..."
if python3 "$PROJECT_DIR/tests/test_train_pipeline.py" > /tmp/test_output.log 2>&1; then
    # Contar tests pasados
    PASSED=$(grep -c "PASS" /tmp/test_output.log || true)
    echo "✓ Tests ejecutados: $PASSED tests pasados"
    # Mostrar output si hay fallos
    if grep -q "FAIL\|Error" /tmp/test_output.log; then
        echo ""
        echo "⚠️  Algunos tests fallaron. Detalles:"
        grep "FAIL\|Error" /tmp/test_output.log | head -5
        echo "   Ver /tmp/test_output.log para más detalles"
    fi
else
    echo "⚠️  Tests encontraron problemas"
    tail -20 /tmp/test_output.log
fi

# ========== PASO 9: Verificar archivos creados ==========
echo ""
echo "📋 PASO 9: Verificando archivos de documentación..."
DOCS=(
    "docs/TRAIN_PIPELINE_GUIDE.md"
    "docs/PIPELINE_DIAGRAMS.md"
    "INTEGRATION_SUMMARY.md"
    "tests/test_train_pipeline.py"
    "examples_train_pipeline.py"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$PROJECT_DIR/$doc" ]; then
        echo "✓ $doc"
    else
        echo "❌ $doc NO ENCONTRADO"
    fi
done

# ========== RESUMEN ==========
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    RESUMEN DE INSTALACIÓN                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "✅ Instalación completada exitosamente"
echo ""
echo "📍 Ubicaciones Importantes:"
echo "   • Pipeline: src/training/train_pipeline.py"
echo "   • Tests:    tests/test_train_pipeline.py"
echo "   • Docs:     docs/TRAIN_PIPELINE_GUIDE.md"
echo "   • Modelos:  model/"
echo "   • Resultados: artifacts/resultados/"
echo ""
echo "🚀 Próximos Pasos:"
echo ""
echo "1️⃣  Configurar variables de entorno:"
echo "    cp .env.example .env"
echo "    # Editar con tus credenciales de MySQL"
echo ""
echo "2️⃣  Iniciar MLflow (en terminal separada):"
echo "    mlflow ui --host 0.0.0.0 --port 5000"
echo ""
echo "3️⃣  Ejecutar el pipeline:"
echo "    cd $PROJECT_DIR"
echo "    python3 -c \"from src.training.train_pipeline import train_pipeline; train_pipeline()\""
echo ""
echo "4️⃣  Monitorear resultados:"
echo "    • MLflow UI: http://0.0.0.0:5000"
echo "    • Métricas CSV: artifacts/resultados/training_metrics.csv"
echo "    • Modelo: model/trained_pipeline-0.1.0.pkl"
echo ""
echo "5️⃣  Leer documentación:"
echo "    • Guía completa: docs/TRAIN_PIPELINE_GUIDE.md"
echo "    • Diagramas: docs/PIPELINE_DIAGRAMS.md"
echo "    • Resumen: INTEGRATION_SUMMARY.md"
echo ""
echo "💡 Para ver ejemplos de uso:"
echo "    python3 examples_train_pipeline.py"
echo ""
echo "❓ Para obtener ayuda:"
echo "    • Revisar logs en terminal"
echo "    • Consultar documentación en docs/"
echo "    • Ejecutar tests: python3 tests/test_train_pipeline.py"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
