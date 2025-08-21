import pandas as pd; import numpy as np;from scipy.stats.mstats import winsorize
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE; from sklearn.decomposition import PCA; from xgboost import XGBClassifier

def cargar_datos(): # dataset
    csv_path = "C:\Users\facuc\OneDrive - UCA\Documentos\Detección_clientes_de_banco\data\bank-additional-full.csv"
    data = pd.read_csv(csv_path, sep=";"); return data

data = cargar_datos()

def detectar_outliers_iqr(serie):
    Q1 = serie.quantile(0.25)
    Q3 = serie.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return (serie < lower_bound) | (serie > upper_bound)

def outliers(data):
    num_vars = ['age', 'campaign', 'previous', 'duration']
    cat_vars = ['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month', 'poutcome']

    for variable in num_vars:
        outliers_mask = detectar_outliers_iqr(data[variable])
        data[f'is_outlier_{variable}'] = outliers_mask
        outliers = data[variable][outliers_mask]

    # drop columnas con is_outliers False en todas las observaciones
    cols = ["is_outlier_euribor3m", "is_outlier_nr.employed", "is_outlier_emp.var.rate", "is_outlier_cons.price.idx"]
    if all(col in data.columns for col in cols):
        data = data.drop(columns = ["is_outlier_euribor3m", "is_outlier_nr.employed", "is_outlier_emp.var.rate", "is_outlier_cons.price.idx"])

    cols_2 = ['is_outlier_age', 'is_outlier_campaign', 'is_outlier_pdays',
            'is_outlier_previous', 'is_outlier_duration', 'is_outlier_cons.conf.idx']

    # Filtramos solo las columnas que realmente están en el DataFrame
    existing_cols = [col for col in cols_2 if col in data.columns]

    # Aplicamos .any() solo sobre esas columnas
    data['is_outlier'] = data[existing_cols].any(axis=1)

    # Total de contactos
    data['contactosTotales'] = data['campaign'] + data['previous']

    data['is_outlier'] = data['is_outlier']

def encoding(data):
    encode = data 
    encode.drop(columns=['is_outlier', 'default',"poutcome"], inplace=True) # Eliminamos las columnas que no se utilizarán en el encoding

    """## target"""
    encode['y'] = encode['y'].astype(str)
    encode['y'] = encode['y'].map({'no': 0, 'yes': 1})

    """## occupation"""
    categorical_cols = encode.select_dtypes(include=['object']).columns
    cardinality = {}

    # Convertir las columnas categóricas a tipo 'category' para optimizar memoria
    for col in categorical_cols:
        cardinality[col] = encode[col].nunique()

    """### previous"""
    #Binning de previous
    encode['previous_bin'] = pd.cut(data['previous'], bins=[-1, 0, 2, np.inf], labels=[0, 1, 2])
    encode["previous_bin"] = encode["previous_bin"].astype(int)
    encode["previous_bin"].value_counts()
    # 0: Nada (0 contactos), 1: Poco (1 o 2 contactos), 2: Mucho (3-7)

    """### Job"""
    job_target_mean = encode.groupby('job')['y'].mean()
    encode['job_target_mean'] = encode['job'].map(job_target_mean)
    encode.drop('job', axis=1, inplace=True)

    """### Marital"""
    marital_dummies = pd.get_dummies(encode['marital'], prefix='marital', dtype=int)
    encode = pd.concat([encode, marital_dummies], axis=1)
    encode.drop('marital', axis=1, inplace=True)

    """### Education"""
    education_counts = encode['education'].value_counts(normalize=True)
    encode['education_freq_encode'] = encode['education'].map(education_counts)
    encode.drop('education', axis=1, inplace=True)

    """### Housing, Loan y Contact"""
    housing_dummies = pd.get_dummies(encode['housing'], prefix='housing', dtype=int)
    loan_dummies = pd.get_dummies(encode['loan'], prefix='loan', dtype=int)
    contact_dummies = pd.get_dummies(encode['contact'], prefix='contact', dtype=int)
    encode = pd.concat([encode, housing_dummies, loan_dummies, contact_dummies], axis=1)
    encode.drop(['housing', 'loan', 'contact'], axis=1, inplace=True)

    """### Month y Day of Week"""
    month_mapping = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    encode['month'] = encode['month'].map(month_mapping)
    day_mapping = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5}
    encode['day_of_week'] = encode['day_of_week'].map(day_mapping)
    return encode

"""### Sacar outliers"""
def remove_outliers_iqr(df):
    df_no_outliers = df
    numeric_cols = df_no_outliers.select_dtypes(include=np.number).columns # Filter for numeric columns only
    for col in numeric_cols: # Iterate over numeric columns
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df_no_outliers = df_no_outliers[(df_no_outliers[col] >= lower_bound) & (df_no_outliers[col] <= upper_bound)]
    return df_no_outliers

def pca_smote(encode):
    x = encode
    smote_df = x.copy()
    smote_df_y = smote_df['y']
    smote_df_x = smote_df.drop('y', axis=1)

    smote = SMOTE(sampling_strategy = 0.3, random_state=42)
    X_resampled, y_resampled = smote.fit_resample(smote_df_x, smote_df_y)

    # PCA
    X = X_resampled; y = y_resampled

    scaler = StandardScaler(); X = scaler.fit_transform(X) # creamos el escalador y lo aplicamos a X

    pca = PCA(); X_pca = pca.fit_transform(X) # aplicamos PCA sin especificar n_components para ver la varianza explicada

    pca = PCA(n_components=15); X_pca = pca.fit_transform(X) # aplicamos PCA con 15 componentes principales
    return X_pca, y

def modelo(x, y):
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    xgb_model = XGBClassifier(
        n_estimators=100, learning_rate=0.1, max_depth=6,
        eval_metric='logloss', random_state=42)
    
    # Ajustar el modelo
    xgb_model.fit(X_train, y_train)

    y_pred = xgb_model.predict(X_test); y_proba = xgb_model.predict_proba(X_test)[:, 1] # predección y probabilidad de la clase 1

    # Crear DataFrame ordenado por probabilidad de clase 1
    df_resultados = pd.DataFrame({
        'Índice': range(len(X_test)),
        'Probabilidad_clase_1': y_proba,
        'Predicción': y_pred,
        'Real': y_test.values
    })

    df_ordenado = df_resultados.sort_values(by='Probabilidad_clase_1', ascending=False).reset_index(drop=True)
    return df_ordenado