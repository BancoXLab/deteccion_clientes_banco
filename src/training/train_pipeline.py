import os
import pymysql
import logging
import pickle
from pathlib import Path
import pandas as pd
from sklearn.utils import resample
from dotenv import load_dotenv
from sqlalchemy import create_engine
from imblearn.over_sampling import SMOTE
from prefect import flow, task, get_run_logger
from pathlib import Path
from src.training.esquema_DB_train import definir_esquema_prepared
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)
import mlflow
import mlflow.xgboost
import mlflow.sklearn

# Cargar variables de entorno
load_dotenv()

# Carpeta temporal para Parquet (configurable vía env `BANCX_TMP_DIR`)
import os

TMP_DIR = Path(os.getenv("BANCX_TMP_DIR", "/tmp/bancox_train"))
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Directorios de modelos y resultados
MODEL_DIR = Path(os.getenv("BANCX_MODEL_DIR", "/workspaces/deteccion_clientes_banco/model"))
MODEL_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_DIR = Path(os.getenv("BANCX_RESULTS_DIR", "/workspaces/deteccion_clientes_banco/artifacts/resultados"))
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://0.0.0.0:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Ruta del modelo en producción
PRODUCTION_MODEL_PATH = MODEL_DIR / "trained_pipeline-0.1.0.pkl"


# --------------------------------------------------------
# Prefect Tasks
# --------------------------------------------------------

@task(name="Cargar datos desde MySQL", retries=2, retry_delay_seconds=30, timeout_seconds=600)
def load_data():
    """Carga los datos desde la base de datos MySQL y los guarda como parquet."""
    logger = get_run_logger()
    logger.info(" Conectando a la base de datos para cargar datos...")

    try:
        engine = create_engine(
            f"mysql+pymysql://{os.getenv('user')}:{os.getenv('password')}"
            f"@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('db')}"
        )

        df = pd.read_sql_table(table_name="BancoX", con=engine)
        logger.info(f" Datos cargados: {df.shape[0]} filas y {df.shape[1]} columnas.")

        path = TMP_DIR / "dataset_raw.parquet"
        df.to_parquet(path, index=False)
        logger.info(f" Guardado temporalmente en {path}")

        return str(path)

    except Exception as e:
        logger.error(f" Error al cargar los datos: {e}")
        raise

def _safe_logger():
    # Devuelve un logger de Prefect si hay contexto, o un logger estándar
    try:
        return get_run_logger()
    except Exception:
        return logging.getLogger(__name__)

def apply_smote_raw(input_path: str, target_col: str = "y", target_per_class: int = 10000) -> str:
    """
    Oversampling aleatorio hasta `target_per_class` por clase (mínimo).
    Devuelve la ruta del parquet resultante.
    """

    df = pd.read_parquet(input_path)
    if target_col not in df.columns:
        raise ValueError(f"{target_col} no está en las columnas del dataframe")

    counts = df[target_col].value_counts()
    max_n = counts.max()
    # forzar mínimo por clase
    target_n = max(max_n, int(target_per_class))

    parts = []
    for _, grp in df.groupby(target_col):
        if len(grp) >= target_n:
            parts.append(grp.sample(target_n, replace=False, random_state=0))
        else:
            parts.append(grp.sample(target_n, replace=True, random_state=0))

    df_res = pd.concat(parts).reset_index(drop=True)

    out_path = TMP_DIR / "smote_output.parquet"
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    df_res.to_parquet(out_path, index=False)
    return str(out_path)

@task(name="Aplicar SMOTE", retries=1, retry_delay_seconds=20, timeout_seconds=900)
def apply_smote(path_raw: str):
    """Realiza oversampling con SMOTE y guarda el resultado como parquet."""
    logger = get_run_logger()
    logger.info(" Iniciando oversampling con SMOTE...")

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

        logger.info(f" SMOTE completo: {df_resampled.shape[0]} filas. Guardado en {path}")
        return str(path)

    except Exception as e:
        logger.error(f" Error durante el oversampling: {e}")
        raise


@task(name="Guardar datos en MySQL", retries=2, retry_delay_seconds=30, timeout_seconds=1200)
def save_transformed_data(path_resampled: str):
    """Guarda los datos SMOTEados en una nueva tabla MySQL."""
    logger = get_run_logger()
    logger.info(" Conectando para insertar datos transformados...")

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
        logger.info(f" Datos insertados correctamente. Total registros en DB: {count_db:,}")

    except Exception as e:
        logger.error(f" Error al insertar los datos: {e}")

def clean_temp_files_raw(tmp_dir: str = None) -> None:
    """
    Lógica pura para limpiar archivos temporales.
    """
    dirp = Path(tmp_dir) if tmp_dir else TMP_DIR
    for p in dirp.glob("*.parquet"):
        try:
            p.unlink()
        except FileNotFoundError:
            pass


@task(name="Limpieza temporal")
def clean_temp_files():
    """Elimina los archivos temporales parquet si todo salió bien."""
    logger = get_run_logger()
    for f in TMP_DIR.glob("*.parquet"):
        try:
            f.unlink()
            logger.info(f" Archivo temporal eliminado: {f}")
        except Exception as e:
            logger.warning(f" No se pudo eliminar {f}: {e}")


# --------------------------------------------------------
# Funciones de entrenamiento y evaluación
# --------------------------------------------------------

def _train_model(model_type: str, X_train, Y_train, X_test):
    """Entrena un modelo según el tipo especificado."""
    if model_type == "XGBoost":
        params = {
            "n_estimators": 100,
            "learning_rate": 0.1,
            "max_depth": 6,
            "eval_metric": "logloss",
            "random_state": 42
        }
        model = XGBClassifier(**params)
    elif model_type == "Random Forest":
        params = {
            "n_estimators": 500,
            "max_depth": 10,
            "random_state": 42
        }
        model = RandomForestClassifier(**params)
    elif model_type == "Logistic Regression":
        params = {
            "max_iter": 1000,
            "solver": "liblinear",
            "random_state": 42
        }
        model = LogisticRegression(**params)
    else:
        raise ValueError(f"Modelo no soportado: {model_type}")
    
    model.fit(X_train, Y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    return model, params, y_pred, y_prob


def _calculate_metrics(Y_test, y_pred, y_prob, Y_train, y_pred_train):
    """Calcula todas las métricas de desempeño."""
    metrics = {
        "accuracy": accuracy_score(Y_test, y_pred),
        "recall": recall_score(Y_test, y_pred),
        "precision": precision_score(Y_test, y_pred),
        "f1": f1_score(Y_test, y_pred),
        "roc_auc": roc_auc_score(Y_test, y_prob),
        "accuracy_train": accuracy_score(Y_train, y_pred_train)
    }
    return metrics


def _load_production_model_f1() -> float:
    """Carga el F1 score del modelo en producción."""
    logger = logging.getLogger(__name__)
    
    if not PRODUCTION_MODEL_PATH.exists():
        logger.warning(" No hay modelo en producción. F1 de referencia será 0.")
        return 0.0
    
    try:
        with open(PRODUCTION_MODEL_PATH, "rb") as f:
            production_model = pickle.load(f)
        
        # Si el modelo tiene un atributo f1_score, usarlo
        if hasattr(production_model, 'f1_score'):
            return production_model.f1_score
        else:
            logger.warning(" Modelo en producción no tiene F1 score registrado. Usando 0.")
            return 0.0
    except Exception as e:
        logger.error(f" Error cargando modelo de producción: {e}")
        return 0.0


@task(name="Entrenar modelo de clasificación", retries=1, retry_delay_seconds=30, timeout_seconds=1800)
def train_classification_model(path_resampled: str, model_type: str = "XGBoost"):
    """
    Entrena un modelo de clasificación, calcula métricas y las registra con MLflow.
    Compara F1 score con modelo en producción.
    """
    logger = get_run_logger()
    logger.info(f" Iniciando entrenamiento del modelo {model_type}...")
    
    try:
        # Cargar datos
        df = pd.read_parquet(path_resampled)
        train, test = train_test_split(df, test_size=0.2, random_state=42)
        
        X_train = train.drop("y", axis=1)
        Y_train = train["y"]
        X_test = test.drop("y", axis=1)
        Y_test = test["y"]
        
        logger.info(f" Train shape: {X_train.shape}, Test shape: {X_test.shape}")
        
        # Entrenar modelo
        model, params, y_pred, y_prob = _train_model(model_type, X_train, Y_train, X_test)
        y_pred_train = model.predict(X_train)
        
        # Calcular métricas
        metrics = _calculate_metrics(Y_test, y_pred, y_prob, Y_train, y_pred_train)
        
        # Obtener F1 score del modelo en producción
        production_f1 = _load_production_model_f1()
        new_f1 = metrics["f1"]
        f1_improvement = new_f1 - production_f1
        should_deploy = f1_improvement > 0.0
        
        logger.info(f" Métricas calculadas - F1: {new_f1:.4f}, F1 Producción: {production_f1:.4f}")
        logger.info(f" Mejora F1: {f1_improvement:.4f}, Debe actualizar: {should_deploy}")
        
        # Registrar con MLflow
        mlflow.set_experiment(f"BancoX-{model_type}")
        with mlflow.start_run(run_name=f"{model_type}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"):
            # Log de parámetros
            mlflow.log_params(params)
            
            # Log de métricas
            mlflow.log_metrics(metrics)
            mlflow.log_metric("f1_production", production_f1)
            mlflow.log_metric("f1_improvement", f1_improvement)
            mlflow.log_param("should_deploy", should_deploy)
            
            # Log del modelo
            if model_type == "XGBoost":
                mlflow.xgboost.log_model(model, "model")
            else:
                mlflow.sklearn.log_model(model, "model")
            
            # Log de información adicional
            mlflow.log_text(f"Train samples: {len(X_train)}\nTest samples: {len(X_test)}", "data_info.txt")
            
            logger.info(f" Modelo registrado en MLflow con run_id: {mlflow.active_run().info.run_id}")
        
        # Guardar métricas en CSV
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        metrics_record = pd.DataFrame([{
            "timestamp": timestamp,
            "modelo": model_type,
            "accuracy": round(metrics["accuracy"], 4),
            "recall": round(metrics["recall"], 4),
            "precision": round(metrics["precision"], 4),
            "f1": round(metrics["f1"], 4),
            "accuracy_train": round(metrics["accuracy_train"], 4),
            "roc_auc": round(metrics["roc_auc"], 4),
            "f1_production": round(production_f1, 4),
            "f1_improvement": round(f1_improvement, 4),
            "should_deploy": should_deploy
        }])
        
        metrics_file = RESULTS_DIR / "training_metrics.csv"
        if metrics_file.exists():
            metrics_record.to_csv(metrics_file, mode="a", header=False, index=False)
        else:
            metrics_record.to_csv(metrics_file, index=False)
        
        logger.info(f" Métricas guardadas en {metrics_file}")
        
        return {
            "model": model,
            "metrics": metrics,
            "should_deploy": should_deploy,
            "f1_improvement": f1_improvement,
            "model_type": model_type
        }
        
    except Exception as e:
        logger.error(f" Error durante el entrenamiento: {e}")
        raise


@task(name="Guardar modelo si mejora")
def save_model_if_improved(training_result: dict):
    """
    Guarda el modelo en producción si el F1 score mejoró.
    """
    logger = get_run_logger()
    
    if not training_result["should_deploy"]:
        logger.info(f" No hay mejora en F1 ({training_result['f1_improvement']:.4f}). Modelo no será actualizado.")
        return False
    
    try:
        model = training_result["model"]
        f1_improvement = training_result["f1_improvement"]
        
        # Guardar con timestamp de backup
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        backup_path = MODEL_DIR / f"model_backup_{timestamp}.pkl"
        
        # Hacer backup del modelo anterior si existe
        if PRODUCTION_MODEL_PATH.exists():
            import shutil
            shutil.copy(PRODUCTION_MODEL_PATH, backup_path)
            logger.info(f" Backup del modelo anterior guardado en {backup_path}")
        
        # Guardar nuevo modelo
        with open(PRODUCTION_MODEL_PATH, "wb") as f:
            pickle.dump(model, f)
        
        # Guardar metadatos
        metadata = {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_type": training_result["model_type"],
            "f1_score": round(training_result["metrics"]["f1"], 4),
            "f1_improvement": round(f1_improvement, 4),
            "accuracy": round(training_result["metrics"]["accuracy"], 4),
            "recall": round(training_result["metrics"]["recall"], 4),
            "precision": round(training_result["metrics"]["precision"], 4),
            "roc_auc": round(training_result["metrics"]["roc_auc"], 4)
        }
        
        metadata_file = MODEL_DIR / "model_metadata.txt"
        import json
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f" ✅ Modelo actualizado en {PRODUCTION_MODEL_PATH}")
        logger.info(f" Mejora en F1: +{f1_improvement:.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f" Error al guardar el modelo: {e}")
        raise


# --------------------------------------------------------
# Prefect Flow principal
# --------------------------------------------------------

@flow(name="Pipeline de entrenamiento BancoX")
def train_pipeline(model_type: str = "XGBoost"):
    """
    Flujo principal: carga datos, aplica SMOTE, entrena modelo,
    evalúa mejora y actualiza en producción si corresponde.
    
    Args:
        model_type: Tipo de modelo a entrenar ("XGBoost", "Random Forest", "Logistic Regression")
    """
    logger = get_run_logger()
    logger.info(f" Iniciando pipeline de entrenamiento BancoX con modelo {model_type}...")

    # Cargar y transformar datos
    path_raw = load_data()
    path_resampled = apply_smote(path_raw)
    save_transformed_data(path_resampled)
    
    # Entrenar modelo
    training_result = train_classification_model(path_resampled, model_type)
    
    # Guardar modelo si mejora
    model_updated = save_model_if_improved(training_result)
    
    # Limpiar archivos temporales
    clean_temp_files()

    logger.info(f" Pipeline completado con éxito ✅")
    logger.info(f" Modelo actualizado en producción: {model_updated}")


# --------------------------------------------------------
# Ejecución directa
# --------------------------------------------------------

if __name__ == "__main__":
    # Ejecutar con modelo XGBoost (por defecto)
    train_pipeline.serve(
        name="Entrenamiento BancoX",
        cron="0 3 * * *",  # Ejecuta diariamente a las 3:00 AM
        tags=["produccion", "mlflow-tracking"]
    )
