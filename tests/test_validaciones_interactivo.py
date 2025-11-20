#!/usr/bin/env python3
"""
Script para probar validaciones de forma interactiva
Muestra exactamente qué mensajes de error ve el usuario
"""

import json
from pydantic import BaseModel, field_validator, ValidationError
from typing import Dict, Any

# ===== COPIAMOS LA CONFIGURACIÓN DEL main_orq.py =====

FIELD_TYPES = {
    "int_fields": [
        "month", "day_of_week", "previous_bin",
        "marital_divorced", "marital_married", "marital_single", "marital_unknown",
        "housing_no", "housing_unknown", "housing_yes",
        "loan_no", "loan_unknown", "loan_yes",
        "contact_cellular", "contact_telephone"
    ],
    "float_fields": [
        "age", "duration", "campaign", "pdays", "previous",
        "emp_var_rate", "cons_price_idx", "cons_conf_idx", "euribor3m", "nr_employed",
        "job_target_mean", "education_freq_encode"
    ]
}

FIELD_RANGES = {
    "age": (0, 120),
    "month": (1, 12),
    "day_of_week": (1, 7),
    "duration": (0, 5000),
    "campaign": (0, 100),
    "pdays": (-1, 999),
    "previous": (0, 100),
    "previous_bin": (0, 1),
    "marital_divorced": (0, 1),
    "marital_married": (0, 1),
    "marital_single": (0, 1),
    "marital_unknown": (0, 1),
    "housing_no": (0, 1),
    "housing_unknown": (0, 1),
    "housing_yes": (0, 1),
    "loan_no": (0, 1),
    "loan_unknown": (0, 1),
    "loan_yes": (0, 1),
    "contact_cellular": (0, 1),
    "contact_telephone": (0, 1),
}

class ClientData(BaseModel):
    age: float
    month: int
    day_of_week: int
    duration: float
    campaign: float
    pdays: float
    previous: float
    emp_var_rate: float
    cons_price_idx: float
    cons_conf_idx: float
    euribor3m: float
    nr_employed: float
    previous_bin: int
    job_target_mean: float
    marital_divorced: int
    marital_married: int
    marital_single: int
    marital_unknown: int
    education_freq_encode: float
    housing_no: int
    housing_unknown: int
    housing_yes: int
    loan_no: int
    loan_unknown: int
    loan_yes: int
    contact_cellular: int
    contact_telephone: int

    @field_validator("*", mode="before")
    @classmethod
    def validar_no_nulo(cls, value: Any, info) -> Any:
        field_name = info.field_name
        if value is None:
            raise ValueError(
                f"❌ Campo '{field_name}' está vacío o nulo. "
                f"Este campo es requerido y no puede estar vacío."
            )
        return value

    @field_validator("*", mode="before")
    @classmethod
    def validar_tipo(cls, value: Any, info) -> Any:
        field_name = info.field_name
        if field_name in FIELD_TYPES["int_fields"]:
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(
                    f"   Campo '{field_name}' debe ser un número ENTERO (int).\n"
                    f"   Recibió: {type(value).__name__} = {value}\n"
                    f"   Ejemplos válidos: 0, 1, 2, 12, -1"
                )
        elif field_name in FIELD_TYPES["float_fields"]:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(
                    f"   Campo '{field_name}' debe ser un número (int o float).\n"
                    f"   Recibió: {type(value).__name__} = {value}\n"
                    f"   Ejemplos válidos: 25.5, 100, 3.14, -1.5"
                )
        return value

    @field_validator("*", mode="after")
    @classmethod
    def validar_rango(cls, value: Any, info) -> Any:
        field_name = info.field_name
        if field_name in FIELD_RANGES:
            min_val, max_val = FIELD_RANGES[field_name]
            if not (min_val <= value <= max_val):
                raise ValueError(
                    f"❌ Campo '{field_name}' está fuera de rango permitido.\n"
                    f"   Rango válido: [{min_val}, {max_val}]\n"
                    f"   Valor recibido: {value}\n"
                    f"   💡 Verifica que el valor sea correcto."
                )
        return value


# Datos válidos de plantilla
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


def print_resultado(titulo: str, data: Dict, success: bool = False):
    """Imprime un resultado de prueba de forma legible."""
    print("\n" + "="*80)
    print(titulo)
    print("="*80)
    
    if success:
        print("✅ VALIDACIÓN EXITOSA")
    else:
        print("❌ VALIDACIÓN FALLIDA")
    
    print("\nDatos enviados:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_valido():
    """Test 1: Datos completamente válidos"""
    print_resultado("TEST 1: ✅ Datos Válidos", VALID_DATA)
    try:
        result = ClientData(**VALID_DATA)
        print("\n✅ RESULTADO: La validación pasó exitosamente")
        print(f"   Edad: {result.age}")
        print(f"   Mes: {result.month}")
        print(f"   Predicción esperada: Se puede proceder")
    except ValidationError as e:
        print(f"❌ Error: {e}")


def test_age_string():
    """Test 2: Age como string"""
    data = {**VALID_DATA, "age": "treinta y cinco"}
    print_resultado("TEST 2: ❌ Tipo Incorrecto - 'age' como STRING", data)
    
    try:
        result = ClientData(**data)
        print("✅ Validación pasó (no esperado)")
    except (ValidationError, TypeError) as e:
        print("\n🔴 ERROR DE VALIDACIÓN CAPTURADO:")
        if isinstance(e, ValidationError):
            for error in e.errors():
                field = error.get("loc", ("desconocido",))[0]
                msg = error.get("msg", "Error desconocido")
                print(f"\n   Campo: {field}")
                print(f"   Mensaje: {msg}")
        else:
            print(f"   {str(e)}")


def test_age_nulo():
    """Test 3: Age nulo"""
    data = {**VALID_DATA, "age": None}
    print_resultado("TEST 3: ❌ Valor Nulo - 'age' es None", data)
    
    try:
        result = ClientData(**data)
        print("✅ Validación pasó (no esperado)")
    except (ValidationError, TypeError, ValueError) as e:
        print("\n🔴 ERROR DE VALIDACIÓN CAPTURADO:")
        if isinstance(e, ValidationError):
            for error in e.errors():
                field = error.get("loc", ("desconocido",))[0]
                msg = error.get("msg", "Error desconocido")
                print(f"\n   Campo: {field}")
                print(f"   Mensaje: {msg}")
        else:
            print(f"   {str(e)}")


def test_month_fuera_rango():
    """Test 4: Month fuera de rango"""
    data = {**VALID_DATA, "month": 13}
    print_resultado("TEST 4: ❌ Valor Fuera de Rango - 'month' = 13 (válido 1-12)", data)
    
    try:
        result = ClientData(**data)
        print("✅ Validación pasó (no esperado)")
    except ValidationError as e:
        print("\n🔴 ERROR DE VALIDACIÓN CAPTURADO:")
        for error in e.errors():
            field = error.get("loc", ("desconocido",))[0]
            msg = error.get("msg", "Error desconocido")
            print(f"\n   Campo: {field}")
            print(f"   Mensaje: {msg}")


def test_month_float():
    """Test 5: Month como float"""
    data = {**VALID_DATA, "month": 3.5}
    print_resultado("TEST 5: ❌ Tipo Incorrecto - 'month' como FLOAT (debe ser INT)", data)
    
    try:
        result = ClientData(**data)
        print("✅ Validación pasó (no esperado)")
    except (ValidationError, TypeError) as e:
        print("\n🔴 ERROR DE VALIDACIÓN CAPTURADO:")
        if isinstance(e, ValidationError):
            for error in e.errors():
                field = error.get("loc", ("desconocido",))[0]
                msg = error.get("msg", "Error desconocido")
                print(f"\n   Campo: {field}")
                print(f"   Mensaje: {msg}")
        else:
            print(f"   {str(e)}")


def test_binary_invalid():
    """Test 6: Campo binario con valor inválido"""
    data = {**VALID_DATA, "marital_married": 2}
    print_resultado("TEST 6: ❌ Valor Fuera de Rango - 'marital_married' = 2 (válido 0-1)", data)
    
    try:
        result = ClientData(**data)
        print("✅ Validación pasó (no esperado)")
    except ValidationError as e:
        print("\n🔴 ERROR DE VALIDACIÓN CAPTURADO:")
        for error in e.errors():
            field = error.get("loc", ("desconocido",))[0]
            msg = error.get("msg", "Error desconocido")
            print(f"\n   Campo: {field}")
            print(f"   Mensaje: {msg}")


def test_age_negativo():
    """Test 7: Age negativo (fuera de rango)"""
    data = {**VALID_DATA, "age": -5}
    print_resultado("TEST 7: ❌ Valor Fuera de Rango - 'age' = -5 (válido 0-120)", data)
    
    try:
        result = ClientData(**data)
        print("✅ Validación pasó (no esperado)")
    except ValidationError as e:
        print("\n🔴 ERROR DE VALIDACIÓN CAPTURADO:")
        for error in e.errors():
            field = error.get("loc", ("desconocido",))[0]
            msg = error.get("msg", "Error desconocido")
            print(f"\n   Campo: {field}")
            print(f"   Mensaje: {msg}")


def test_falta_campo():
    """Test 8: Falta un campo requerido"""
    data = {k: v for k, v in VALID_DATA.items() if k != "age"}
    print_resultado("TEST 8: ❌ Campo Requerido Faltante - Falta 'age'", data)
    
    try:
        result = ClientData(**data)
        print("✅ Validación pasó (no esperado)")
    except ValidationError as e:
        print("\n🔴 ERROR DE VALIDACIÓN CAPTURADO:")
        for error in e.errors():
            field = error.get("loc", ("desconocido",))[0]
            msg = error.get("msg", "Error desconocido")
            print(f"\n   Campo: {field}")
            print(f"   Mensaje: {msg}")


def main():
    print("\n" + "="*80)
    print("🧪 PRUEBAS DE VALIDACIÓN DE ENTRADA - BANCO X API".center(80))
    print("="*80)
    print("""
Este script demuestra exactamente qué mensajes de error verá el usuario
cuando envíe datos inválidos a la API.

Cada test valida un tipo diferente de error:
  1. Datos válidos ✅
  2. Tipo incorrecto (string en lugar de número)
  3. Valor nulo (None)
  4. Valor fuera de rango
  5. Tipo incorrecto (float en lugar de int)
  6. Valor binario inválido
  7. Rango negativo no válido
  8. Campo requerido faltante
    """)
    
    tests = [
        test_valido,
        test_age_string,
        test_age_nulo,
        test_month_fuera_rango,
        test_month_float,
        test_binary_invalid,
        test_age_negativo,
        test_falta_campo,
    ]
    
    for i, test_func in enumerate(tests, 1):
        try:
            test_func()
        except Exception as e:
            print(f"Error en test {i}: {e}")
        
        input("\n⏸️  Presiona ENTER para el siguiente test...")
    
    print("\n" + "="*80)
    print("✅ PRUEBAS COMPLETADAS".center(80))
    print("="*80)
    print("""
RESUMEN:
  • Los mensajes de error son CLAROS y ESPECÍFICOS
  • Se indica exactamente qué tipo de error ocurrió
  • Se muestran los valores válidos y los rangos permitidos
  • El usuario sabe exactamente qué corregir
    """)


if __name__ == "__main__":
    main()
