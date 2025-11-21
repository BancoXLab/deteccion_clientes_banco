import streamlit as st
import requests
import pandas as pd
from typing import List
import os

st.set_page_config(page_title="Banco X - Predictor", page_icon="", layout="wide")

st.title("Banco X - Predictor de Suscripción")

# API URL configuration

DEFAULT_API_URL = os.getenv("BANCO_X_API_URL", "http://fastapi:8000")

if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL

# Sidebar
with st.sidebar:
    st.header("Configuración")
    st.session_state.api_url = st.text_input("URL API", value=st.session_state.api_url)
    
    if st.button("Verificar Conexión"):
        try:
            resp = requests.get(f"{st.session_state.api_url}/healthz", timeout=5)
            if resp.status_code == 200:
                st.success("Conectado")
                info = requests.get(f"{st.session_state.api_url}/info", timeout=5).json()
                st.write(info)
        except Exception as e:
            st.error(f"Error: {str(e)}")

tab1, tab2 = st.tabs(["Individual", "Lote CSV"])

with tab1:
    st.header("Predicción Individual")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        age = st.number_input("Edad", 0, 120, 35)
        month = st.slider("Mes", 1, 12, 5)
        day_of_week = st.slider("Día Semana", 1, 7, 3)
        duration = st.number_input("Duración (s)", 0.0, value=100.0)
        campaign = st.number_input("Campañas", 0.0, value=1.0)
        pdays = st.number_input("Días último contacto", -1.0, value=-1.0)
        previous = st.number_input("Contactos previos", 0.0, value=0.0)
        education_freq_encode = st.number_input("Educación", value=0.3)
    
    with col2:
        emp_var_rate = st.number_input("Tasa Var. Empleo", value=1.1)
        cons_price_idx = st.number_input("Índice Precio", value=93.5)
        cons_conf_idx = st.number_input("Índice Confianza", value=-36.4)
        euribor3m = st.number_input("Euribor 3m", value=1.0)
        nr_employed = st.number_input("Empleados", value=5191.0)
        previous_bin = st.selectbox("Contacto anterior", [0, 1])
        job_target_mean = st.number_input("Media trabajo", value=0.4)
    
    with col3:
        st.subheader("Estado Civil")
        marital_divorced = st.checkbox("Divorciado", False)
        marital_married = st.checkbox("Casado", False)
        marital_single = st.checkbox("Soltero", True)
        marital_unknown = st.checkbox("Desconocido", False)
        
        st.subheader("Vivienda")
        housing_no = st.checkbox("Sin vivienda", False)
        housing_unknown = st.checkbox("Vivienda desconocida", False)
        housing_yes = st.checkbox("Con vivienda", True)
        
        st.subheader("Préstamo")
        loan_no = st.checkbox("Sin préstamo", True)
        loan_unknown = st.checkbox("Préstamo desconocido", False)
        loan_yes = st.checkbox("Con préstamo", False)
        
        st.subheader("Contacto")
        contact_cellular = st.checkbox("Celular", True)
        contact_telephone = st.checkbox("Teléfono", False)
    
    if st.button("Predecir", use_container_width=True, type="primary"):
        try:
            client = {
                "age": float(age),
                "month": int(month),
                "day_of_week": int(day_of_week),
                "duration": float(duration),
                "campaign": float(campaign),
                "pdays": float(pdays),
                "previous": float(previous),
                "emp_var_rate": float(emp_var_rate),
                "cons_price_idx": float(cons_price_idx),
                "cons_conf_idx": float(cons_conf_idx),
                "euribor3m": float(euribor3m),
                "nr_employed": float(nr_employed),
                "previous_bin": int(previous_bin),
                "job_target_mean": float(job_target_mean),
                "marital_divorced": int(marital_divorced),
                "marital_married": int(marital_married),
                "marital_single": int(marital_single),
                "marital_unknown": int(marital_unknown),
                "education_freq_encode": float(education_freq_encode),
                "housing_no": int(housing_no),
                "housing_unknown": int(housing_unknown),
                "housing_yes": int(housing_yes),
                "loan_no": int(loan_no),
                "loan_unknown": int(loan_unknown),
                "loan_yes": int(loan_yes),
                "contact_cellular": int(contact_cellular),
                "contact_telephone": int(contact_telephone),
            }
            
            response = requests.post(f"{st.session_state.api_url}/predict", json=[client], timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                st.json(result)
            else:
                st.error(f"Error: {response.text}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab2:
    st.header("Predicciones por Lote")
    
    uploaded_file = st.file_uploader("CSV con clientes", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write(f"Registros: {len(df)}")
        st.dataframe(df.head())
        
        if st.button("Procesar Lote", type="primary"):
            try:
                clientes = df.to_dict('records')
                
                for cliente in clientes:
                    for key in cliente:
                        if pd.notna(cliente[key]):
                            if key in ['month', 'day_of_week', 'previous_bin', 
                                      'marital_divorced', 'marital_married', 'marital_single', 'marital_unknown',
                                      'housing_no', 'housing_unknown', 'housing_yes',
                                      'loan_no', 'loan_unknown', 'loan_yes',
                                      'contact_cellular', 'contact_telephone']:
                                cliente[key] = int(cliente[key])
                            else:
                                cliente[key] = float(cliente[key])
                
                with st.spinner("Procesando..."):
                    response = requests.post(f"{st.session_state.api_url}/predict", json=clientes, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Contar clientes procesados vs predichos como positivos
                    total_enviados = len(clientes)
                    total_positivos = len(result)
                    
                    st.success(f"{total_enviados} clientes procesados")
                    
                    result_df = pd.DataFrame(result)
                    st.dataframe(result_df)
                    
                    csv = result_df.to_csv(index=False)
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name="predicciones.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(f"Error: {response.text}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
