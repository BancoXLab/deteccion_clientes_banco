from prefect import flow, task, get_run_logger
import pandas as pd
import numpy as np 
import os
import pymysql
from dotenv import load_dotenv
from sklearn.pipeline import Pipeline
from sqlalchemy import create_engine
from imblearn.over_sampling import SMOTE


load_dotenv()

@task(name = "Carga de datos")
def load_data():
    """
    Carga los datos desde la base de datos MySQL.
    """
    logger = get_run_logger()
    
    timeout = 100
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

    try:
        df = pd.read_sql_table(
            table_name="BancoX",
            con=engine
        )
        logger.info(f"Datos cargados: {df.shape[0]} filas y {df.shape[1]} columnas.")
    except Exception as e:
        logger.error(f"Error al cargar los datos: {e}")
    finally:
        connection.close()

    return df


@task(name="Transformaciones de datos")
def transformations(df):
    """
    Realiza un oversampling a los datos para que estos queden listos para ser usados por el modelo, en caso de que esto no se aplique, simplemente no se corre el flow.
    """
    logger = get_run_logger()

    # oversampling del dataset
    df_to_smote = df.drop(columns=['y'])
    y = df['y']

    smote = SMOTE(sampling_strategy={1:10000}, random_state=42, k_neighbors=5)
    logger.info("Iniciando oversampling con SMOTE...")

    X_resampled, y_resampled = smote.fit_resample(df_to_smote, y)

    df_resampled = pd.DataFrame(X_resampled, columns=df_to_smote.columns)
    df_resampled["y"] = y_resampled

    logger.info(f"Datos después de SMOTE: {df_resampled.shape[0]} filas y {df_resampled.shape[1]} columnas.")
    return df_resampled

@flow(name="Pipeline de entrenamientoy guardado")
def train_pipeline():
    logger = get_run_logger()
    logger.info("Iniciando flujo de entrenamiento...")

    # Cargar datos
    data = load_data()

    # Transformar
    transformed_data = transformations(data)
    logger.info(f"Datos transformados: {transformed_data.shape[0]} filas y {transformed_data.shape[1]} columnas.")

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

    try:
        transformed_data.to_sql(
            name="BancoX_prepared_data",
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



if __name__ == "__main__":
    train_pipeline.serve(name="Pipeline de entrenamiento", cron="* * * * *")