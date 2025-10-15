import os
import pymysql
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine
from imblearn.over_sampling import SMOTE

# Cargar variables de entorno
load_dotenv()

# --------------------------------------------------------
# Carga de datos desde MySQL
# --------------------------------------------------------
def load_data():
    """
    Carga los datos desde la base de datos MySQL.
    """
    print("📥 Cargando datos desde MySQL...")
    
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
        df = pd.read_sql_table(table_name="BancoX", con=engine)
        print(f"✅ Datos cargados: {df.shape[0]} filas y {df.shape[1]} columnas.")
    except Exception as e:
        print(f"❌ Error al cargar los datos: {e}")
        df = pd.DataFrame()  # Devuelve vacío si falla
    finally:
        connection.close()

    return df

# --------------------------------------------------------
# Transformaciones de datos (SMOTE)
# --------------------------------------------------------
def apply_smote(df):
    """
    Realiza oversampling con SMOTE para balancear la clase objetivo.
    """
    print("🔄 Iniciando oversampling con SMOTE...")

    try:
        X = df.drop(columns=["y"])
        y = df["y"]

        smote = SMOTE(sampling_strategy={1: 10000}, random_state=42, k_neighbors=5)
        X_resampled, y_resampled = smote.fit_resample(X, y)

        df_resampled = pd.DataFrame(X_resampled, columns=X.columns)
        df_resampled["y"] = y_resampled

        print(f"✅ Oversampling completo: {df_resampled.shape[0]} filas y {df_resampled.shape[1]} columnas.")
        return df_resampled

    except Exception as e:
        print(f"❌ Error durante el oversampling: {e}")
        return df

# --------------------------------------------------------
# Escritura de los datos transformados
# --------------------------------------------------------
def save_transformed_data(df):
    """
    Escribe los datos preparados en una nueva tabla MySQL.
    """
    print("💾 Guardando datos transformados en la base de datos...")

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
        df.to_sql(
            name="BancoX_prepared_data",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi"
        )
        print("✅ Datos insertados correctamente en BancoX_prepared_data.")
    except Exception as e:
        print(f"❌ Error al insertar los datos: {e}")
    finally:
        connection.close()

# --------------------------------------------------------
# Pipeline principal
# --------------------------------------------------------
def train_pipeline():
    print("🚀 Iniciando pipeline de entrenamiento...")

    df = load_data()
    if df.empty:
        print("⚠️ No se cargaron datos. Pipeline cancelado.")
        return

    df_transformed = apply_smote(df)
    save_transformed_data(df_transformed)

    print("🏁 Pipeline completado con éxito.")


# --------------------------------------------------------
# Ejecución directa
# --------------------------------------------------------
if __name__ == "__main__":
    train_pipeline()
