import streamlit as st
import pandas as pd
import plotly.express as px
import string

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Auditoría Logística Last Mile", layout="wide")

st.title("📦 Panel de Control de Calidad de Reparto")
st.markdown("Sube el reporte de entregas para analizar el desempeño de los repartidores.")

# --- 1. CARGA DE DATOS ---
archivo = st.sidebar.file_uploader("Sube tu archivo Excel (.xlsx)", type=['xlsx'])

if archivo:
    # Definimos nombres de columnas estándar (A-Q) para evitar errores de nombres cambiantes
    column_names = list(string.ascii_uppercase[:17])
    
    try:
        # Leemos el archivo cargado directamente
        df = pd.read_excel(archivo, names=column_names, header=0)
        
        # --- 2. PROCESAMIENTO ---
        # H=Repartidor | L=Estado (donde buscamos 'entregado') | O=CP
        
        # Conteo total de envíos por repartidor
        repartidor_counts = df['H'].value_counts().reset_index()
        repartidor_counts.columns = ['Repartidor', 'Total_Envios']
        
        # Filtrado de éxitos: buscamos la palabra 'entregado' en la columna L
        # Usamos case=False para que no importe si es 'Entregado' o 'ENTREGADO'
        efectivos = df[df['L'].astype(str).str.contains('entregado', na=False, case=False)]
        
        exitos_counts = efectivos['H'].value_counts().reset_index()
        exitos_counts.columns = ['Repartidor', 'Entregas_Exitosas'] # <--- Nombre unificado
        
        # Unión de datos (Merge)
        resumen_repartidores = pd.merge(repartidor_counts, exitos_counts, on='Repartidor', how='left').fillna(0)
        
        # --- CORRECCIÓN LÍNEA 37 ---
        # Calculamos el % de efectividad usando el nombre unificado
        resumen_repartidores['Efectividad_%'] = (resumen_repartidores['Entregas_Exitosas'] / resumen_repartidores['Total_Envios'] * 100).round(2)
        
        # --- 3. VISUALIZACIÓN ---
        
        # Métricas rápidas en la parte superior
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Pedidos", len(df))
        m2.metric("Entregas Exitosas", int(resumen_repartidores['Entregas_Exitosas'].sum()))
        m3.metric("Efectividad Global", f"{resumen_repartidores['Efectividad_%'].mean():.1f}%")
        
        st.divider()
        
        # Gráfico Comparativo de Repartidores
        st.subheader("🏎️ Rendimiento por Repartidor")
        fig_repa = px.bar(
            resumen_repartidores.sort_values('Total_Envios', ascending=False), 
            x='Repartidor', 
            y=['Total_Envios', 'Entregas_Exitosas'],
            barmode='group',
            labels={'value': 'Cantidad de Paquetes', 'variable': 'Estado'},
            color_discrete_map={'Total_Envios': '#1f77b4', 'Entregas_Exitosas': '#2ca02c'}
        )
        st.plotly_chart(fig_repa, use_container_width=True)
        
        # Distribución por Código Postal
        st.subheader("📍 Concentración por Código Postal (Top 15)")
        cp_data = df['O'].value_counts().head(15).reset_index()
        cp_data.columns = ['CP', 'Pedidos']
        fig_cp = px.pie(cp_data, values='Pedidos', names='CP', hole=0.3)
        st.plotly_chart(fig_cp, use_container_width=True)
        
        # Tabla detallada
        st.subheader("📋 Detalle de Auditoría")
        st.dataframe(resumen_repartidores.sort_values('Efectividad_%', ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"Hubo un error al procesar el archivo: {e}")
        st.info("Asegúrate de que el Excel tenga el formato de columnas esperado.")

else:
    st.info("👋 Por favor, carga un archivo Excel en la barra lateral para comenzar el análisis.")
