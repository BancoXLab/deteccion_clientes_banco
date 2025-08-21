import streamlit as st
from mvp_con_frontend import cargar_datos, outliers, encoding, pca_smote, modelo


st.set_page_config(page_title="Modelo Marketing", layout="centered")
st.title("🧠 Generador de candidatos a clientes")

if st.button("Generar candidatos"):
    with st.spinner("Procesando..."):
        data = cargar_datos()
        outliers(data)
        encode = encoding(data)
        X_pca, y = pca_smote(encode)
        resultado = modelo(X_pca, y)
    
    st.success("Mejores candidatos generados con éxito!")
    st.dataframe(resultado.head(100))