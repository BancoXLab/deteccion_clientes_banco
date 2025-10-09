import os
import pymysql
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.datasets import fetch_openml
from sklearn.preprocessing import FunctionTransformer
from encoding import enc_preprocessor
from esquema_DB import definir_esquema
from prefect import flow, task

load_dotenv()

# ingesta 
def ingesta():
    """
    Ingesta de datos desde OpenML
    """
    source = fetch_openml(data_id=42813, as_frame=True)  # marketing bancario
    data = pd.DataFrame(source.data)
    data["y"] = data['y'].map({"no": 0, "yes": 1}) # se mapea Y de primera 
    
    return data


# transformaciones aplicadas ------------------------------------------------------------------------------------------

# detección simple de duplicados
def remove_duplicates(df, y=None):
    return df.drop_duplicates(), y # se eliminan duplicados pero no por id debido a que no hay id

duplicados_transformer = FunctionTransformer(remove_duplicates)

# insertar datos en la base de datos ------------------------------------------------------------------------------------------
def escritura():
    """
    Escribe los datos procesados en la base de datos
    """
    dataset = ingesta()
    
    y = dataset["y"]
    X = dataset.drop(columns="y")
    
    # aplicar preprocesamiento
    preprocessor = enc_preprocessor()
    X_clean = preprocessor.fit_transform(X)

    # recuperar nombres de columnas transformadas
    feature_names = preprocessor.get_feature_names_out()
    X_clean_df = pd.DataFrame(X_clean, columns=feature_names)
    X_clean_df["y"] = y.values  # volver a agregar target

    # limpiar nombres de columnas para SQL
    cols = []
    for col in X_clean_df.columns:
        if 'num__' in col:
            cols.append(col.replace('num__', ''))    
        elif 'cat__' in col:
            cols.append(col.replace('cat__', '').replace('x0_', ''))
        elif 'ord__' in col:
            cols.append(col.replace('ord__', ''))
    
    X_clean_df = pd.DataFrame(X_clean, columns=cols)

    dataset_clean = pd.concat([X_clean_df, y], axis=1)

    dataset_clean = dataset_clean.rename(columns={
          "emp.var.rate": "emp_var_rate",
          "cons.price.idx": "cons_price_idx",
          "cons.conf.idx": "cons_conf_idx",
          "nr.employed": "nr_employed",
          "job_admin.": "job_admin",
          "job_blue-collar": "job_blue_collar",
          "job_self-employed": "job_self_employed"
      })

    # conexión a la DB
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
        f"mysql+pymysql://{os.getenv('user')}:{os.getenv('password')}@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('db')}"
    )

    metadata, BancoX = definir_esquema()
    metadata.create_all(engine)  # Crear la tabla si no existe

    try:
      dataset_clean.to_sql(
          name="BancoX",
          con=engine,
          if_exists="append",
          index=False,
          chunksize=1000,
          method="multi"
      )
      print("Datos insertados correctamente.")
    except Exception as e:
      print(f"Error al insertar los datos: {e}")
    connection.close()


escritura()
