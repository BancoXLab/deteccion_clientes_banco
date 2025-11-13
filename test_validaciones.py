#!/usr/bin/env python3
"""
Script de prueba para validar el endpoint /predict con diferentes errores
Demuestra cómo el sistema maneja errores de entrada y da mensajes claros.
"""

import json
from pydantic import ValidationError

# Datos de entrada válidos (plantilla)
VALID_DATA = {
    "age": 35,
    "month": 3,
    "day_of_week": 2,
    "duration": 250,
    "campaign": 1,
    "pdays": -1,
    "previous": 0,
    "emp_var_rate": 1.1,
    "cons_price_idx": 93.5,
    "cons_conf_idx": -42.0,
    "euribor3m": 0.75,
    "nr_employed": 5099.1,
    "previous_bin": 0,
    "job_target_mean": 0.5,
    "marital_divorced": 0,
    "marital_married": 1,
    "marital_single": 0,
    "marital_unknown": 0,
    "education_freq_encode": 2.0,
    "housing_no": 0,
    "housing_unknown": 0,
    "housing_yes": 1,
    "loan_no": 1,
    "loan_unknown": 0,
    "loan_yes": 0,
    "contact_cellular": 1,
    "contact_telephone": 0,
}

# Casos de prueba para demostrar los mensajes de error
TEST_CASES = [
    {
        "name": "✅ CASO 1: Datos válidos",
        "data": VALID_DATA,
        "expected": "success"
    },
    {
        "name": "❌ CASO 2: Tipo incorrecto en 'age' (string en lugar de float)",
        "data": {**VALID_DATA, "age": "treinta y cinco"},
        "expected": "validation_error"
    },
    {
        "name": "❌ CASO 3: Campo 'month' nulo",
        "data": {**VALID_DATA, "month": None},
        "expected": "validation_error"
    },
    {
        "name": "❌ CASO 4: 'month' fuera de rango (valor: 13)",
        "data": {**VALID_DATA, "month": 13},
        "expected": "validation_error"
    },
    {
        "name": "❌ CASO 5: 'month' como float en lugar de int",
        "data": {**VALID_DATA, "month": 3.5},
        "expected": "validation_error"
    },
    {
        "name": "❌ CASO 6: 'day_of_week' fuera de rango (valor: 8)",
        "data": {**VALID_DATA, "day_of_week": 8},
        "expected": "validation_error"
    },
    {
        "name": "❌ CASO 7: 'age' fuera de rango (valor: 150)",
        "data": {**VALID_DATA, "age": 150},
        "expected": "validation_error"
    },
    {
        "name": "❌ CASO 8: 'marital_married' debe ser 0 o 1, recibe 2",
        "data": {**VALID_DATA, "marital_married": 2},
        "expected": "validation_error"
    },
    {
        "name": "❌ CASO 9: Falta campo requerido (falta 'age')",
        "data": {k: v for k, v in VALID_DATA.items() if k != "age"},
        "expected": "validation_error"
    },
    {
        "name": "❌ CASO 10: 'campaign' como string",
        "data": {**VALID_DATA, "campaign": "cinco"},
        "expected": "validation_error"
    },
]


def print_test_case(case, result):
    """Imprime el resultado de una prueba de forma legible."""
    print("\n" + "="*70)
    print(f"📋 {case['name']}")
    print("="*70)
    
    if isinstance(result, dict) and "detail" in result:
        detail = result["detail"]
        print(f"Status Code: {result.get('status_code', 'N/A')}")
        print(f"Tipo de error: {detail.get('status', 'UNKNOWN')}")
        print(f"Mensaje: {detail.get('message', detail.get('error', 'N/A'))}")
        
        if "details" in detail:
            print("\nDetalles de validación:")
            for err in detail["details"]:
                print(f"  - Campo: {err['field']}")
                print(f"    Tipo de error: {err['error_type']}")
                print(f"    Mensaje: {err['message']}")
    elif isinstance(result, dict) and "success" in result:
        if result["success"]:
            print(f"✅ Predicción exitosa!")
            print(f"Resultado: {result['prediction_label']}")
            print(f"Score: {result['prediction']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    """Ejecuta los casos de prueba."""
    print("\n" + "🔍 PRUEBAS DE VALIDACIÓN DE ENTRADA".center(70))
    print("="*70)
    
    print("\n📌 Información útil:")
    print("  • Los campos se validan por tipo (int vs float)")
    print("  • Se validan rangos según el tipo de dato")
    print("  • Ningún campo puede ser NULL/None")
    print("  • Se proporcionan mensajes claros indicando el error")
    print("  • Cada error incluye: tipo, valor recibido y ejemplos válidos")
    
    print("\n" + "-"*70)
    print("INSTRUCCIONES PARA PROBAR EN LA API REAL:")
    print("-"*70)
    print("""
1. Iniciar el servidor:
   $ uvicorn scr.app.main_orq:app --reload --port 8000

2. En otra terminal, ejecutar las pruebas:
   $ python test_validaciones.py

3. O probar con curl desde otra terminal:

   # Caso válido:
   curl -X POST "http://localhost:8000/predict" \\
     -H "Content-Type: application/json" \\
     -d '{}' (usar datos de VALID_DATA)

   # Caso con error:
   curl -X POST "http://localhost:8000/predict" \\
     -H "Content-Type: application/json" \\
     -d '{"age": "treinta", ...}'

4. O usar en Python:
   
   import requests
   
   data = {...}  # usar VALID_DATA o casos de prueba
   response = requests.post("http://localhost:8000/predict", json=data)
   print(response.json())
    """)
    
    print("\n" + "-"*70)
    print("EJEMPLOS DE RESPUESTAS DE ERROR:")
    print("-"*70)
    
    # Mostrar estructura de errores
    error_response_example = {
        "success": False,
        "error": "Validación de datos fallida",
        "details": [
            {
                "field": "age",
                "error_type": "value_error",
                "message": "❌ Campo 'age' está fuera de rango permitido...",
            }
        ],
        "status": "VALIDATION_ERROR",
        "hint": "Revisa los campos señalados y verifica tipos y rangos."
    }
    
    print(json.dumps(error_response_example, indent=2, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("📊 CAMPOS REQUERIDOS Y TIPOS ESPERADOS")
    print("="*70)
    
    fields_info = {
        "Campos ENTEROS (0, 1, 2, ...)": [
            "month (1-12)", "day_of_week (1-7)", "previous_bin (0-1)",
            "marital_* (0-1)", "housing_* (0-1)", "loan_* (0-1)", 
            "contact_* (0-1)"
        ],
        "Campos FLOTANTES (1.5, 3.14, -2.0, ...)": [
            "age (0-120)", "duration", "campaign", "pdays", "previous",
            "emp_var_rate", "cons_price_idx", "cons_conf_idx", 
            "euribor3m", "nr_employed", "job_target_mean", "education_freq_encode"
        ]
    }
    
    for category, fields in fields_info.items():
        print(f"\n{category}:")
        for field in fields:
            print(f"  ✓ {field}")


if __name__ == "__main__":
    main()
