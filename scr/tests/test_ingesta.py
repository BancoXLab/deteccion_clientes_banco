# tests/test_ingesta.py
import pandas as pd
from scr.ingesta.Ingesta_de_datos import remove_duplicates_raw
from prefect.testing.utilities import prefect_test_harness

def test_remove_duplicates_creates_file(tmp_path):
    df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 3, 4]})
    input_file = tmp_path / "raw.parquet"
    df.to_parquet(input_file)
    
    result_path = remove_duplicates_raw(str(input_file))
    df_result = pd.read_parquet(result_path)
    assert len(df_result) == 2
