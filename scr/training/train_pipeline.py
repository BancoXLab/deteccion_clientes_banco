import os
import pymysql
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from imblearn.over_sampling import SMOTE
from prefect import flow, task, get_run_logger
from pathlib import Path
from esquema_DB_train import definir_esquema_prepared

# Cargar variables de entorno
load_dotenv()

# Carpeta temporal para Parquet
TMP_DIR = Path("/tmp/bancox_train")
TMP_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------
# Prefect Tasks
# --------------------------------------------------------

@task(name="Cargar datos desde MySQL", retries=2, retry_delay_seconds=30, timeout_seconds=600)
def load_data():
    """Carga los datos desde la base de datos MySQL y los guarda como parquet."""
    logger = get_run_logger()
    logger.info("📥 Conectando a la base de datos para cargar datos...")

    try:
        engine = create_engine(
            f"mysql+pymysql://{os.getenv('user')}:{os.getenv('password')}"
            f"@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('db')}"
        )

        df = pd.read_sql_table(table_name="BancoX", con=engine)
        logger.info(f"✅ Datos cargados: {df.shape[0]} filas y {df.shape[1]} columnas.")

        path = TMP_DIR / "dataset_raw.parquet"
        df.to_parquet(path, index=False)
        logger.info(f"📦 Guardado temporalmente en {path}")

        return str(path)

    except Exception as e:
        logger.error(f"❌ Error al cargar los datos: {e}")
        raise


@task(name="Aplicar SMOTE", retries=1, retry_delay_seconds=20, timeout_seconds=900)
def apply_smote(path_raw: str):
    """Realiza oversampling con SMOTE y guarda el resultado como parquet."""
    logger = get_run_logger()
    logger.info("🔄 Iniciando oversampling con SMOTE...")

    try:
        df = pd.read_parquet(path_raw)
        X = df.drop(columns=["y"])
        y = df["y"]

        smote = SMOTE(sampling_strategy={1: 10000}, random_state=42, k_neighbors=5)
        X_resampled, y_resampled = smote.fit_resample(X, y)

        df_resampled = pd.DataFrame(X_resampled, columns=X.columns)
        df_resampled["y"] = y_resampled

        path = TMP_DIR / "dataset_resampled.parquet"
        df_resampled.to_parquet(path, index=False)

        logger.info(f"✅ SMOTE completo: {df_resampled.shape[0]} filas. Guardado en {path}")
        return str(path)

    except Exception as e:
        logger.error(f"❌ Error durante el oversampling: {e}")
        raise


@task(name="Guardar datos en MySQL", retries=2, retry_delay_seconds=30, timeout_seconds=1200)
def save_transformed_data(path_resampled: str):
    """Guarda los datos SMOTEados en una nueva tabla MySQL."""
    logger = get_run_logger()
    logger.info("💾 Conectando para insertar datos transformados...")

    df = pd.read_parquet(path_resampled)
    engine = create_engine(
        f"mysql+pymysql://{os.getenv('user')}:{os.getenv('password')}"
        f"@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('db')}"
    )

    # Crear la tabla si no existe, con PRIMARY KEY
    metadata, BancoX_prepared = definir_esquema_prepared()
    metadata.create_all(engine)

    try:
        df.to_sql(
            name="BancoX_prepared_data",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi"
        )

        count_db = pd.read_sql("SELECT COUNT(*) AS total FROM BancoX_prepared_data", con=engine).iloc[0, 0]
        logger.info(f"✅ Datos insertados correctamente. Total registros en DB: {count_db:,}")

    except Exception as e:
        logger.error(f"❌ Error al insertar los datos: {e}")


@task(name="Limpieza temporal")
def clean_temp_files():
    """Elimina los archivos temporales parquet si todo salió bien."""
    logger = get_run_logger()
    for f in TMP_DIR.glob("*.parquet"):
        try:
            f.unlink()
            logger.info(f"🧹 Archivo temporal eliminado: {f}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo eliminar {f}: {e}")


# --------------------------------------------------------
# Prefect Flow principal
# --------------------------------------------------------

@flow(name="Pipeline de entrenamiento BancoX")
def train_pipeline():
    """Flujo principal: carga datos, aplica SMOTE y guarda resultados."""
    logger = get_run_logger()
    logger.info("🚀 Iniciando pipeline de entrenamiento BancoX...")

    path_raw = load_data()
    path_resampled = apply_smote(path_raw)
    save_transformed_data(path_resampled)
    clean_temp_files()

    logger.info("🏁 Pipeline completado con éxito ✅")


# --------------------------------------------------------
# Ejecución directa
# --------------------------------------------------------

if __name__ == "__main__":
    train_pipeline.serve(name="Entrenamiento BancoX", cron="0 3 * * *")
