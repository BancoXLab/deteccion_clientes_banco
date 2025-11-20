import pandas as pd
from prefect.testing.utilities import prefect_test_harness
from scr.ingesta.Ingesta_de_datos import remove_duplicates_raw
from scr.training.train_pipeline import apply_smote_raw

def test_prefect_like_flow(tmp_path):
    # preparar datos
    df = pd.DataFrame({"x1":[1,2,3,4],"x2":[1,2,3,4],"y":[0,0,1,1]})
    f = tmp_path / "d.parquet"
    df.to_parquet(f)

    # ejecutar dentro del contexto de test de Prefect
    with prefect_test_harness():
        nodup = remove_duplicates_raw(str(f))
        out = apply_smote_raw(nodup, target_col="y", target_per_class=4)
        df_out = pd.read_parquet(out)
        assert "y" in df_out.columns