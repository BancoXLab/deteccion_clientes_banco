from sqlalchemy import Table, Column, Integer, Float, String, MetaData



def definir_esquema():
    # Crear metadata
    metadata = MetaData()

    # Definir la tabla en Python
    BancoX = Table(
        "BancoX", metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("age", Integer),
        Column("duration", Integer),
        Column("campaign", Integer),
        Column("pdays", Integer),
        Column("previous", Integer),
        Column("emp_var_rate", Float),
        Column("cons_price_idx", Float),
        Column("cons_conf_idx", Float),
        Column("euribor3m", Float),
        Column("nr_employed", Float),
        Column("education", String(50)),
        Column("month", String(10)),
        Column("day_of_week", String(10)),
        Column("job_admin", String(3)),
        Column("job_blue_collar", String(3)),
        Column("job_entrepreneur", String(3)),
        Column("job_housemaid", String(3)),
        Column("job_management", String(3)),
        Column("job_retired", String(3)),
        Column("job_self_employed", String(3)),
        Column("job_services", String(3)),
        Column("job_student", String(3)),
        Column("job_technician", String(3)),
        Column("job_unemployed", String(3)),
        Column("job_unknown", String(3)),
        Column("marital_divorced", String(3)),
        Column("marital_married", String(3)),
        Column("marital_single", String(3)),
        Column("marital_unknown", String(3)),
        Column("default_no", String(3)),
        Column("default_unknown", String(3)),
        Column("default_yes", String(3)),
        Column("housing_no", String(3)),
        Column("housing_unknown", String(3)),
        Column("housing_yes", String(3)),
        Column("loan_no", String(3)),
        Column("loan_unknown", String(3)),
        Column("loan_yes", String(3)),
        Column("contact_cellular", String(3)),
        Column("contact_telephone", String(3)),
        Column("poutcome_failure", String(3)),
        Column("poutcome_nonexistent", String(3)),
        Column("poutcome_success", String(3)),
        Column("y", Integer)
    )

    return metadata, BancoX