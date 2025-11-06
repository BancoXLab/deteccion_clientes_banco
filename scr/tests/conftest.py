# ...existing code...
from scr.ingesta.Ingesta_de_datos import load_data  # adapta si el nombre difiere
from scr.utils.pii import anonymize_dataframe

def test_ingesta_y_ofuscacion(sample_df):
    df = sample_df
    df2 = anonymize_dataframe(df, {"email":"email","name":"name"})
    assert "email" in df2.columns
    assert df2["email"].iloc[0] != df["email"].iloc[0]
# ...existing code...