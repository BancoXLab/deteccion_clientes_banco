# tests/test_train_pipeline.py
import pandas as pd
from src.training.train_pipeline import apply_smote_raw, clean_temp_files_raw, TMP_DIR

def test_apply_smote_balances_classes(tmp_path):
    df = pd.DataFrame({
        "x1": [1, 2, 3, 4],
        "x2": [10, 20, 30, 40],
        "y": [0, 0, 1, 1]
    })
    input_file = tmp_path / "data.parquet"
    df.to_parquet(input_file)

    output_path = apply_smote_raw(str(input_file))
    df_res = pd.read_parquet(output_path)

    assert "y" in df_res.columns
    assert df_res["y"].value_counts().min() >= 10000 or len(df_res) > len(df)

def test_clean_temp_files_removes_parquet(tmp_path):
    dummy = tmp_path / "dummy.parquet"
    dummy.write_text("test")
    clean_temp_files_raw(tmp_path)
    assert not dummy.exists()
