#!/usr/bin/env bash
set -euo pipefail
# Script batch stub: ejecuta funciones raw para ETL local y guarda salida
python - <<'PY'
from pathlib import Path
import pandas as pd
from scr.ingesta.Ingesta_de_datos import remove_duplicates_raw
from scr.training.train_pipeline import apply_smote_raw

tmp = Path("/tmp/bancox_batch_example")
tmp.mkdir(parents=True, exist_ok=True)
# crear ejemplo
df = pd.DataFrame({"x1":[1,1,2,3],"x2":[10,10,20,30],"y":[0,0,1,1]})
infile = tmp/"input.parquet"
df.to_parquet(infile)

# ✅ sin out_dir, ya guarda en la misma carpeta
nodup = remove_duplicates_raw(str(infile))
out = apply_smote_raw(nodup, target_col="y", target_per_class=10)
print("Batch finished. output:", out)
PY