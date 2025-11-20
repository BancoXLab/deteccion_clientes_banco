import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import json

# Integración con el sistema de monitoreo existente
ALERTS_LOG = Path("scr/ops/alerts.log")
METRICS_PATH = Path("resultados/metrics.csv")

def load_alerts():
    if not ALERTS_LOG.exists():
        return pd.DataFrame(columns=["timestamp", "level", "metric", "value", "threshold", "details"])
    
    alerts = []
    with open(ALERTS_LOG) as f:
        for line in f:
            parts = line.strip().split(" | ")
            if len(parts) >= 4:
                alert = {
                    "timestamp": datetime.now(),  # En producción usar timestamp real
                    "level": parts[0],
                    "metric": parts[1],
                    "value": float(parts[2].split("=")[1]),
                    "threshold": float(parts[3].split("=")[1]),
                    "details": parts[4] if len(parts) > 4 else ""
                }
                alerts.append(alert)
    return pd.DataFrame(alerts)

def plot_metrics(df_alerts):
    if df_alerts.empty:
        st.info("No hay alertas registradas")
        return

    # Gráfica de métricas en el tiempo
    fig = go.Figure()
    for metric in df_alerts["metric"].unique():
        df_metric = df_alerts[df_alerts["metric"] == metric]
        fig.add_trace(go.Scatter(
            x=df_metric["timestamp"],
            y=df_metric["value"],
            name=metric,
            mode="lines+markers"
        ))
    
    fig.update_layout(
        title="Métricas de Monitoreo",
        xaxis_title="Tiempo",
        yaxis_title="Valor",
        height=400
    )
    st.plotly_chart(fig)

def display_alerts(df_alerts):
    if df_alerts.empty:
        return
    
    # Mostrar alertas críticas primero
    df_sorted = df_alerts.sort_values(["level", "timestamp"], ascending=[False, False])
    
    for _, alert in df_sorted.iterrows():
        color = "🔴" if alert["level"] == "CRITICAL" else "🟡"
        st.write(f"{color} **{alert['level']}**: {alert['metric']}")
        st.write(f"Valor: {alert['value']:.2f} (umbral: {alert['threshold']:.2f})")
        if alert["details"]:
            st.write(f"Detalles: {alert['details']}")
        st.write("---")

def main():
    st.set_page_config(page_title="Monitor de Sistema", layout="wide")
    st.title("📊 Monitor de Sistema")

    # Cargar datos
    df_alerts = load_alerts()
    
    # Dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Métricas en Tiempo Real")
        plot_metrics(df_alerts)
        
        if Path(METRICS_PATH).exists():
            st.subheader("Métricas del Modelo")
            df_metrics = pd.read_csv(METRICS_PATH)
            st.dataframe(df_metrics)
    
    with col2:
        st.subheader("Alertas Activas")
        display_alerts(df_alerts)

if __name__ == "__main__":
    main()