from pydantic import BaseModel, field_validator
from typing import Any

# Mapeo de tipos de campos y rangos válidos (compartido por la app)
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
    """Modelo de entrada con validación exhaustiva y mensajes de error claros."""

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
                f"Campo '{field_name}' está vacío o nulo. Este campo es requerido y no puede estar vacío."
            )
        return value

    @field_validator("*", mode="before")
    @classmethod
    def validar_tipo(cls, value: Any, info) -> Any:
        field_name = info.field_name
        if field_name in FIELD_TYPES["int_fields"]:
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(
                    f"Campo '{field_name}' debe ser un número ENTERO (int). Recibió: {type(value).__name__} = {value}"
                )
        elif field_name in FIELD_TYPES["float_fields"]:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(
                    f"Campo '{field_name}' debe ser un número (int o float). Recibió: {type(value).__name__} = {value}"
                )
        return value

    @field_validator("*", mode="after")
    @classmethod
    def validar_rango(cls, value: Any, info) -> Any:
        field_name = info.field_name
        if field_name in FIELD_RANGES:
            min_val, max_val = FIELD_RANGES[field_name]
            try:
                if not (min_val <= value <= max_val):
                    raise ValueError(
                        f"Campo '{field_name}' fuera de rango [{min_val}, {max_val}]. Valor: {value}"
                    )
            except TypeError:
                # Si la comparación falla por tipo, dejar que la validación de tipo lo capture
                pass
        return value
