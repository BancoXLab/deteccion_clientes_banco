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


@task(name="Transformar datos")
def transformar(dataset):
    """Aplica encoding y limpieza para la base SQL"""
    logger = get_run_logger()

    y = dataset["y"]
    X = dataset.drop(columns="y")

    preprocessor = enc_preprocessor()
    X_clean = preprocessor.fit_transform(X)
    feature_names = preprocessor.get_feature_names_out()
    X_clean_df = pd.DataFrame(X_clean, columns=feature_names)
    X_clean_df["y"] = y.values

    # limpiar nombres de columnas para SQL
    cols = []
    for col in X_clean_df.columns:
        if 'num__' in col:
            cols.append(col.replace('num__', ''))    
        elif 'cat__' in col:
            cols.append(col.replace('cat__', '').replace('x0_', ''))
        elif 'ord__' in col:
            cols.append(col.replace('ord__', ''))
        else:
            cols.append(col)
    X_clean_df.columns = cols

    # renombrar columnas problemáticas
    X_clean_df = X_clean_df.rename(columns={
        "emp.var.rate": "emp_var_rate",
        "cons.price.idx": "cons_price_idx",
        "cons.conf.idx": "cons_conf_idx",
        "nr.employed": "nr_employed",
        "job_admin.": "job_admin",
        "job_blue-collar": "job_blue_collar",
        "job_self-employed": "job_self_employed"
    })

    logger.info("Transformación completada correctamente.")
    return X_clean_df


@task(name="Escritura en la base de datos")
def escritura(dataset_clean):
    """Escribe los datos procesados en MySQL"""
    logger = get_run_logger()

    timeout = 10
    connection = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db=os.getenv("db"),
        host=os.getenv("host"),
        password=os.getenv("password"),
        read_timeout=timeout,
        port=int(os.getenv("port")),
        user=os.getenv("user"),
        write_timeout=timeout,
    )
    
    engine = create_engine(
        f"mysql+pymysql://{os.getenv('user')}:{os.getenv('password')}"
        f"@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('db')}"
    )

    metadata, BancoX = definir_esquema()
    metadata.create_all(engine)

    try:
        dataset_clean.to_sql(
            name="BancoX",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi"
        )
        logger.info("✅ Datos insertados correctamente.")
    except Exception as e:
        logger.error(f"Error al insertar los datos: {e}")
    finally:
        connection.close()

# --------------------------------------------------------
# Prefect flow principal
# --------------------------------------------------------

@flow(name="ETL BancoX - Prefect Flow")
def etl_banco():
    logger = get_run_logger()
    logger.info("Iniciando flujo ETL BancoX...")

    data = ingesta()
    data_no_dupes = remove_duplicates(data)
    data_clean = transformar(data_no_dupes)
    escritura(data_clean)

    logger.info("Flujo ETL completado con éxito ✅")


if __name__ == "__main__":
    etl_banco()