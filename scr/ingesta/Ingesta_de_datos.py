import os
import pymysql
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.datasets import fetch_openml
from scr.ingesta.encoding import enc_preprocessor
from scr.ingesta.esquema_DB import definir_esquema
from prefect import flow, task, get_run_logger
from pathlib import Path
from scr.utils.errors import handle_exceptions


load_dotenv()

TMP_DIR = Path("/tmp/etl_bancox")
TMP_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------
# Prefect Tasks
# --------------------------------------------------------

@task(name="Ingesta de datos")
def ingesta():
    """Descarga el dataset y lo guarda como parquet temporal."""
    logger = get_run_logger()
    logger.info("📥 Descargando dataset desde OpenML...")

    source = fetch_openml(data_id=42813, as_frame=True)
    data = pd.DataFrame(source.data)
    data["y"] = data["y"].map({"no": 0, "yes": 1})

    path = TMP_DIR / "dataset_raw.parquet"
    data.to_parquet(path, index=False)

    logger.info(f"✅ Dataset guardado en {path}, {data.shape[0]} filas.")
    return str(path)


def load_data():
    """Compatibilidad para tests: carga el dataset desde OpenML de forma síncrona
    y guarda un parquet en TMP_DIR, devolviendo la ruta como string.
    Esta función no está decorada con Prefect para que pueda importarse y
    usarse en entornos de testing sin el runtime de Prefect.
    """
    source = fetch_openml(data_id=42813, as_frame=True)
    data = pd.DataFrame(source.data)
    data["y"] = data["y"].map({"no": 0, "yes": 1})

    path = TMP_DIR / "dataset_raw.parquet"
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    data.to_parquet(path, index=False)

    return str(path)


# Decorar las versiones sin Prefect para que los tests y scripts directos
# registren excepciones de forma consistente sin interferir con Prefect.
load_data = handle_exceptions(default=None, reraise=False)(load_data)

def remove_duplicates_raw(path_raw: str):
    """Versión sin Prefect de remove_duplicates para testing"""
    df = pd.read_parquet(path_raw)
    n_before = len(df)
    df = df.drop_duplicates()
    n_after = len(df)
    
    path = Path(path_raw).parent / "dataset_nodupes.parquet"
    df.to_parquet(path, index=False)
    
    return str(path)


# versión no-prefect decorada para manejo uniforme de errores en tests
remove_duplicates_raw = handle_exceptions(default=None, reraise=False)(remove_duplicates_raw)

@task(name="Eliminar duplicados")
def remove_duplicates(path_raw: str):
    """Elimina duplicados y guarda resultado como parquet."""
    logger = get_run_logger()

    df = pd.read_parquet(path_raw)
    n_before = len(df)
    df = df.drop_duplicates()
    n_after = len(df)

    path = TMP_DIR / "dataset_nodupes.parquet"
    df.to_parquet(path, index=False)

    logger.info(f"🧹 Eliminadas {n_before - n_after} filas duplicadas. Guardado en {path}.")
    return str(path)


@task(name="Transformar datos", timeout_seconds=900, retries=2, retry_delay_seconds=30)
def transformar(path_nodupes: str):
    """Aplica encoding y limpieza, guarda dataset limpio como parquet."""
    logger = get_run_logger()
    logger.info("⚙️ Iniciando transformación de datos...")

    dataset = pd.read_parquet(path_nodupes)
    y = dataset["y"]
    X = dataset.drop(columns="y")

    preprocessor = enc_preprocessor()
    X_clean = preprocessor.fit_transform(X)
    feature_names = preprocessor.get_feature_names_out()
    X_clean_df = pd.DataFrame(X_clean, columns=feature_names)
    X_clean_df["y"] = y.values

    # Limpieza de nombres
    replacements = {
        ".": "_",
        "-": "_",
        "num__": "",
        "cat__": "",
        "ord__": "",
        "x0_": "",
    }

    def clean_column(col):
        for old, new in replacements.items():
            col = col.replace(old, new)
        return col

    X_clean_df.columns = [clean_column(col) for col in X_clean_df.columns]

    X_clean_df = X_clean_df.rename(columns={"job_admin_": "job_admin"})

    path = TMP_DIR / "dataset_clean.parquet"
    X_clean_df.to_parquet(path, index=False)

    logger.info(f"✅ Transformación completada. Guardado en {path}. ({X_clean_df.shape[0]} filas)")
    return str(path)


@task(name="Escritura en la base de datos", timeout_seconds=7200, retries=2, retry_delay_seconds=30)
def escritura(path_clean: str, block_size=3000):
    """Carga el parquet limpio en la base de datos por bloques."""
    logger = get_run_logger()
    logger.info(" Conectando a la base de datos...")

    dataset_clean = pd.read_parquet(path_clean)

    from sqlalchemy.engine import URL

    connection_url = URL.create(
        "mysql+pymysql",
        username=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        port=int(12905), 
        database=os.getenv("db")
    )
    logger.info(f" URL de conexión: {connection_url!r}")

    engine = create_engine(connection_url)


    metadata, BancoX = definir_esquema()
    metadata.create_all(engine)

    #try:
    dataset_clean.to_sql(
            name="BancoX",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi"
        )
    logger.info("✅ Datos insertados correctamente en BancoX.")
        # Verificación post-carga
    # except Exception as e:
    #     logger.error(f" Error al insertar los datos: {e}")

    


# --------------------------------------------------------
# Prefect Flow principal
# --------------------------------------------------------

@flow(name="ETL BancoX - Prefect Flow")
def etl_banco():
    logger = get_run_logger()
    logger.info("🚀 Iniciando flujo ETL BancoX...")

    path_raw = ingesta()
    path_nodupes = remove_duplicates(path_raw)
    path_clean = transformar(path_nodupes)
    escritura(path_clean)

    logger.info("🏁 Flujo ETL completado con éxito ✅")

    print(pd.read_parquet(path_clean).columns)


# --------------------------------------------------------
# Ejecución directa
# --------------------------------------------------------

if __name__ == "__main__":
    # correr una vez o servirlo con cron diario
    etl_banco.serve(name="Ingesta BancoX", cron="0 3 * * *")
