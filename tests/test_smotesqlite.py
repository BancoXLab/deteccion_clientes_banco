import pandas as pd
from sqlalchemy import create_engine, text
from src.training.train_pipeline import apply_smote_raw

def test_apply_smote_and_write_sqlite(tmp_path):
    # dataset pequeño con desbalance
    df = pd.DataFrame({
        "x1": [1,2,3,4,5],
        "x2": [10,20,30,40,50],
        "y": [0,0,0,1,1]
    })
    in_file = tmp_path / "input.parquet"
    df.to_parquet(in_file)

    # solicitar oversampling pero con objetivo pequeño para CI
    out_path = apply_smote_raw(str(in_file), target_col="y", target_per_class=10)
    df_res = pd.read_parquet(out_path)

    # comprobar que ahora hay >= target_per_class por clase
    counts = df_res["y"].value_counts()
    assert counts.min() >= 10

    # persistir en SQLite in-memory para comprobar escritura
    engine = create_engine("sqlite:///:memory:")
    df_res.to_sql("train_table", con=engine, index=False)

    # usar conexión para ejecutar la consulta (SQLAlchemy 2.x)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM train_table"))
        n = result.scalar()

    assert n == len(df_res)