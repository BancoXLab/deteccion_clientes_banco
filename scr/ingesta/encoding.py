from prefect import task, flow
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

def enc_preprocessor():
    """
    Devuelve un ColumnTransformer con las transformaciones
    fijas para el dataset del banco.
    """
    # Variables por tipo
    num_features = [
        "age", "duration", "campaign", "pdays", "previous",
        "emp.var.rate", "cons.price.idx", "cons.conf.idx",
        "euribor3m", "nr.employed"
    ]

    ord_features = ["education", "month", "day_of_week"]
    ord_categories = [
        [  # education
            "illiterate", "basic.4y", "basic.6y", "basic.9y",
            "high.school", "professional.course",
            "university.degree", "unknown"
        ],
        [  # month
            "jan", "feb", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec"
        ],
        [  # day_of_week
            "mon", "tue", "wed", "thu", "fri"
        ]
    ]

    cat_features = ["job", "marital", "default", "housing", "loan", "contact", "poutcome"]

    # Construcción del ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", num_features),
            ("ord", OrdinalEncoder(categories=ord_categories), ord_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features)
        ]
    )

    return preprocessor