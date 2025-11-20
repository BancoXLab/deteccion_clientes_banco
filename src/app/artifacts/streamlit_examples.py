"""
Ejemplos de uso de la interfaz de Streamlit

Este archivo contiene ejemplos de datos que puedes usar para probar la aplicación.
"""

# Ejemplo 1: Cliente típico que probablemente se suscribe
CLIENTE_PROBABLE_SUSCRIPCION = {
    "age": 45,
    "month": 5,
    "day_of_week": 3,
    "duration": 300.0,
    "campaign": 1.0,
    "pdays": -1.0,
    "previous": 0.0,
    "emp_var_rate": 1.1,
    "cons_price_idx": 93.5,
    "cons_conf_idx": -36.4,
    "euribor3m": 1.0,
    "nr_employed": 5191.0,
    "previous_bin": 0,
    "job_target_mean": 0.6,
    "marital_divorced": 0,
    "marital_married": 1,
    "marital_single": 0,
    "marital_unknown": 0,
    "education_freq_encode": 0.5,
    "housing_no": 0,
    "housing_unknown": 0,
    "housing_yes": 1,
    "loan_no": 1,
    "loan_unknown": 0,
    "loan_yes": 0,
    "contact_cellular": 1,
    "contact_telephone": 0,
}

# Ejemplo 2: Cliente joven que probablemente no se suscribe
CLIENTE_IMPROBABLE_SUSCRIPCION = {
    "age": 25,
    "month": 11,
    "day_of_week": 1,
    "duration": 30.0,
    "campaign": 3.0,
    "pdays": 999.0,
    "previous": 1.0,
    "emp_var_rate": -1.8,
    "cons_price_idx": 92.0,
    "cons_conf_idx": -46.2,
    "euribor3m": 0.5,
    "nr_employed": 4963.0,
    "previous_bin": 1,
    "job_target_mean": 0.2,
    "marital_divorced": 0,
    "marital_married": 0,
    "marital_single": 1,
    "marital_unknown": 0,
    "education_freq_encode": 0.3,
    "housing_no": 1,
    "housing_unknown": 0,
    "housing_yes": 0,
    "loan_no": 0,
    "loan_unknown": 1,
    "loan_yes": 0,
    "contact_cellular": 0,
    "contact_telephone": 1,
}

# Ejemplo 3: Cliente promedio
CLIENTE_PROMEDIO = {
    "age": 35,
    "month": 6,
    "day_of_week": 2,
    "duration": 150.0,
    "campaign": 2.0,
    "pdays": -1.0,
    "previous": 0.0,
    "emp_var_rate": 0.5,
    "cons_price_idx": 93.0,
    "cons_conf_idx": -40.0,
    "euribor3m": 0.8,
    "nr_employed": 5100.0,
    "previous_bin": 0,
    "job_target_mean": 0.4,
    "marital_divorced": 0,
    "marital_married": 0,
    "marital_single": 1,
    "marital_unknown": 0,
    "education_freq_encode": 0.4,
    "housing_no": 0,
    "housing_unknown": 0,
    "housing_yes": 1,
    "loan_no": 1,
    "loan_unknown": 0,
    "loan_yes": 0,
    "contact_cellular": 1,
    "contact_telephone": 0,
}

if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("EJEMPLOS DE CLIENTES PARA PRUEBAS")
    print("=" * 60)
    
    ejemplos = {
        "probable_suscripcion": CLIENTE_PROBABLE_SUSCRIPCION,
        "improbable_suscripcion": CLIENTE_IMPROBABLE_SUSCRIPCION,
        "cliente_promedio": CLIENTE_PROMEDIO,
    }
    
    for nombre, cliente in ejemplos.items():
        print(f"\n{nombre.upper()}")
        print("-" * 60)
        print(json.dumps(cliente, indent=2))
