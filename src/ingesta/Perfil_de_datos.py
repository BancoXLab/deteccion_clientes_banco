import pandas as pd
from ydata_profiling import ProfileReport

df = pd.read_csv("/workspaces/deteteccion_clientes_banco/data/bank-additional-full.csv", sep=";")

profile = ProfileReport(df)

try:
    profile.to_file("/workspaces/deteteccion_clientes_banco/docs/reporte_perfil.html")
    print("Reporte de perfil de datos generado exitosamente.")
except Exception as e:
    print(f"Error al generar el reporte: {e}")