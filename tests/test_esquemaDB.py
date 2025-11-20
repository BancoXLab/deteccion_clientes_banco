from scr.ingesta.esquema_DB import definir_esquema
from scr.training.esquema_DB_train import definir_esquema_prepared

def test_definir_esquema_has_table():
    metadata, BancoX = definir_esquema()
    assert "BancoX" == BancoX.name
    assert "id" in BancoX.c

def test_definir_esquema_prepared_has_float_columns():
    metadata, BancoX_prep = definir_esquema_prepared()
    assert "BancoX_prepared_data" == BancoX_prep.name
    assert any(col.type.__class__.__name__ == "Float" for col in BancoX_prep.columns)