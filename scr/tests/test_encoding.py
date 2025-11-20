# tests/test_encoding.py
from scr.ingesta.encoding import enc_preprocessor
import pandas as pd

def test_enc_preprocessor_output_shape():
    preprocessor = enc_preprocessor()
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
        "poutcome": ["nonexistent", "success"]
    })
    result = preprocessor.fit_transform(df)
    assert result.shape[0] == 2
    assert result.shape[1] > len(df.columns)
