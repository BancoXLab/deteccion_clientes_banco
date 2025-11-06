import streamlit as st
import pandas as pd
import plotly.express as px

st.title('Dashboard de Suscripciones')

# Cargar CSV
metrics = pd.read_csv("C:/Users/facuc/OneDrive - UCA/Documentos/Detección_clientes_de_banco/models/Resultados/metrics.csv")
segmentos = pd.read_csv('C:/Users/facuc/OneDrive - UCA/Documentos/Detección_clientes_de_banco/models/Resultados/clientes_segmentados.csv')
st.subheader('Métricas del Modelo')
st.dataframe(metrics)

st.subheader('Predicciones por Cliente')
st.dataframe(segmentos.head(50))

# Ejemplo gráfico
fig = px.histogram(segmentos, x='probabilidad_clase_1', title='Distribución de probabilidad')
st.plotly_chart(fig)

fig = px.line(
    metrics, x='date', y=['precision', 'recall', 'roc_auc'],
    title='Evolución del Modelo'
)
st.plotly_chart(fig)

roc_df = pd.read_csv('C:/Users/facuc/OneDrive - UCA/Documentos/Detección_clientes_de_banco/models/Resultados/roc_curve.csv')
pr_df = pd.read_csv('C:/Users/facuc/OneDrive - UCA/Documentos/Detección_clientes_de_banco/models/Resultados/pr_curve.csv')

roc_fig = px.area(
    roc_df, x='fpr', y='tpr',
    title='Curva ROC', labels={'fpr': 'False Positive Rate', 'tpr': 'True Positive Rate'}
)
st.plotly_chart(roc_fig)

pr_fig = px.area(
    pr_df, x='recall_curve', y='precision_curve',
    title='Curva Precision-Recall',
    labels={'recall_curve': 'Recall', 'precision_curve': 'Precision'}
)
st.plotly_chart(pr_fig)

clientes_aceptan = segmentos[segmentos['prediccion'] == 1]

fig = px.histogram(
    clientes_aceptan, x='age',
    title='Edades de clientes que aceptan'
)
st.plotly_chart(fig)

fig2 = px.histogram(
    clientes_aceptan, x='job_target_mean',
    title='Tipo de trabajo (clientes que aceptan)',
    color_discrete_sequence=['#636EFA']
)
st.plotly_chart(fig2)

st.subheader('Impacto en la Campaña')
impact = pd.read_csv('C:/Users/facuc/OneDrive - UCA/Documentos/Detección_clientes_de_banco/models/Resultados/impact.csv')
st.write(impact)

fig = px.bar(
    impact, x='scenario', y='roi_estimado',
    title='Comparación ROI antes y después del modelo'
)
st.plotly_chart(fig)

training_status = pd.read_csv('C:/Users/facuc/OneDrive - UCA/Documentos/Detección_clientes_de_banco/models/Resultados/training_status.csv')
ultimo = training_status.iloc[-1]

st.subheader('Estado del Entrenamiento')
st.write(f"Último entrenamiento: {ultimo['last_training_date']}")
st.write(f"Registros nuevos desde último entrenamiento: {ultimo['n_samples']}")
st.write(f"Desviación del comportamiento (drift): {ultimo['drift_metric']:.2f}")

# jobs = st.multiselect('Selecciona tipo de trabajo', opciones=segmentos['job_target_mean'].unique())
# filtered_df = segmentos[segmentos['job_target_mean'].isin(jobs)] if jobs else segmentos
# st.dataframe(filtered_df)

threshold = st.slider('Umbral de probabilidad', 0.0, 1.0, 0.5)
filtered_df = segmentos[segmentos['probabilidad_clase_1'] >= threshold]
st.write(f"Clientes predichos como aceptación: {len(filtered_df)}")

