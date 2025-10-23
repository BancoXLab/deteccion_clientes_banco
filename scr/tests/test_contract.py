import os
import pandas as pd
from sqlalchemy import Table
from scr.ingesta.esquema_DB import definir_esquema
from scr.training.esquema_DB_train import definir_esquema_prepared
from pathlib import Path

SAMPLE_PQ = Path(os.getenv("CONTRACT_SAMPLE_PQ", "data/sample_parquet_for_contract_check.parquet"))

def sqlalchemy_table_columns(table: Table):
    return [c.name for c in table.columns]

def test_ingesta_schema_matches_dataframe():
    # comprobar que parquet muestra las columnas esperadas para la tabla raw
    if not SAMPLE_PQ.exists():
        # si no hay sample, skipear para evitar falsos positivos en CI
        import pytest
        pytest.skip("No hay SAMPLE_PQ para contract test; exporta CONTRACT_SAMPLE_PQ")
    df = pd.read_parquet(SAMPLE_PQ)
    metadata, BancoX = definir_esquema()
    expected_cols = sqlalchemy_table_columns(BancoX)
    # permitir que la tabla tenga columnas adicionales (si no quieres, usa equality)
    missing = [c for c in expected_cols if c not in df.columns]
    assert not missing, f"Faltan columnas en dataframe respecto al esquema: {missing}"

def test_prepared_schema_matches_feature_count():
    # ejemplo para schema train: comprobar que columnas preparadas incluyen la target 'y'
    metadata_p, BancoX_p = definir_esquema_prepared()
    expected_train_cols = sqlalchemy_table_columns(BancoX_p)
    # chequeo simple: 'y' debe existir y al menos 5 columnas preparadas
    assert "y" in expected_train_cols
    assert len(expected_train_cols) > 5