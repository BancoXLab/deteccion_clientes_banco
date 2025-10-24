import pandas as pd
from pathlib import Path
from scr.ingesta.Ingesta_de_datos import remove_duplicates_raw
from scr.ingesta.encoding import enc_preprocessor

def test_ingesta_to_encoding_roundtrip(tmp_path):
    # crear parquet de entrada
    df = pd.DataFrame({
        "age": [30, 40],
        "duration": [100, 200],
        "campaign": [1, 2],
        "pdays": [10, 20],
        "previous": [0, 1],
        "emp.var.rate": [1.1, 1.4],
        "cons.price.idx": [92.5, 93.1],
        "cons.conf.idx": [-36.4, -39.8],
        "euribor3m": [4.8, 4.3],
        "nr.employed": [5191, 5195],
        "education": ["high.school", "university.degree"],
        "month": ["may", "jun"],
        "day_of_week": ["mon", "tue"],
        "job": ["admin.", "technician"],
        "marital": ["single", "married"],
        "default": ["no", "no"],
        "housing": ["yes", "no"],
        "loan": ["no", "no"],
        "contact": ["cellular", "cellular"],
        "poutcome": ["nonexistent", "success"],
        "y": ["no", "yes"]
    })
    input_file = tmp_path / "raw.parquet"
    df.to_parquet(input_file)

    # llama a la función raw de dedupe
    nodup_path = remove_duplicates_raw(str(input_file))
    df_nodup = pd.read_parquet(nodup_path)

    # aplicar preprocessor
    pre = enc_preprocessor()
    out = pre.fit_transform(df_nodup.drop(columns=["y"]))
    assert out.shape[0] == df_nodup.shape[0]
    assert out.shape[1] >= len(df_nodup.columns) - 1