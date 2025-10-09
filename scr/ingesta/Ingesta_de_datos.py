import os
import pymysql
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.datasets import fetch_openml
from sklearn.preprocessing import FunctionTransformer
from encoding import enc_preprocessor
from esquema_DB import definir_esquema
from prefect import flow, task, get_run_logger
import prefect

load_dotenv()

# --------------------------------------------------------
# Prefect tasks
# --------------------------------------------------------

@task(name="Ingesta de datos")
def ingesta():
    """Ingesta de datos desde OpenML"""
    logger = get_run_logger()
    logger.info("Descargando dataset desde OpenML...")
    source = fetch_openml(data_id=42813, as_frame=True)
    data = pd.DataFrame(source.data)
    data["y"] = data["y"].map({"no": 0, "yes": 1})
    logger.info(f"Datos cargados: {data.shape[0]} filas y {data.shape[1]} columnas.")
    return data


@task(name="Eliminar duplicados")
def remove_duplicates(df):
    """Elimina duplicados (sin ID)"""
    logger = get_run_logger()
    n_before = len(df)
    df = df.drop_duplicates()
    n_after = len(df)
    logger.info(f"Eliminadas {n_before - n_after} filas duplicadas.")
    return df


@task(name="Transformar datos", timeout_seconds=900, retries=2, retry_delay_seconds=30)
def transformar(dataset):
    """Aplica encoding y limpieza para la base SQL"""
    logger = get_run_logger()
    logger.info("Iniciando transformación de datos...")

    y = dataset["y"]
    X = dataset.drop(columns="y")

    preprocessor = enc_preprocessor()
    X_clean = preprocessor.fit_transform(X)
    feature_names = preprocessor.get_feature_names_out()
    X_clean_df = pd.DataFrame(X_clean, columns=feature_names)
    X_clean_df["y"] = y.values

    # Diccionario de reemplazos específicos
    replacements = {
        ".": "_",
        "-": "_",
        "num__": "",
        "cat__": "",
        "ord__": "",
        "x0_": "",
    }

    # Función de limpieza de nombres
    def clean_column(col):
        for old, new in replacements.items():
            col = col.replace(old, new)
        return col

    # Aplicar limpieza
    X_clean_df.columns = [clean_column(col) for col in X_clean_df.columns]

    logger.info("Transformación completada correctamente.")
    return X_clean_df


@task(name="Escritura en la base de datos", timeout_seconds=6600, retries=2, retry_delay_seconds=30)
def escritura(dataset_clean, block_size=3000):
    """Carga por bloques para evitar timeouts en Prefect"""
    logger = get_run_logger()
    logger.info("Conectando a la base de datos...")

    # Engine SQLAlchemy
    engine_url = f"mysql+pymysql://{os.getenv('user')}:{os.getenv('password')}@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('db')}?charset=utf8mb4"
    engine = create_engine(engine_url, pool_pre_ping=True)

    # Crear esquema si no existe
    metadata, BancoX = definir_esquema()
    metadata.create_all(engine)

    # Carga por bloques
    total_rows = len(dataset_clean)
    logger.info(f"Iniciando carga de {total_rows:,} filas en bloques de {block_size:,}...")

    try:
        logger.info("Estoy en el try")
        for start in range(0, total_rows, block_size):
            end = min(start + block_size, total_rows)
            block = dataset_clean.iloc[start:end]
            block.to_sql(
                name="BancoX",
                con=engine,
                if_exists="append",
                index=False,
                method="multi"
            )
        logger.info("✅ Carga completada correctamente.")

    except Exception as e:
        logger.error(f"❌ Error al insertar los datos: {e}")





# --------------------------------------------------------
# Prefect flow principal
# --------------------------------------------------------

@flow(name="ETL BancoX - Prefect Flow")
def etl_banco():
    logger = get_run_logger()
    logger.info("Iniciando flujo ETL BancoX...")

    data = ingesta.submit()
    data_no_dupes = remove_duplicates.submit(data)
    data_clean = transformar.submit(data_no_dupes)
    escritura.submit(data_clean)


    logger.info("Flujo ETL completado con éxito ✅")


if __name__ == "__main__":
    etl_banco.serve(name="Ingesta de datos", cron="* * * * *")