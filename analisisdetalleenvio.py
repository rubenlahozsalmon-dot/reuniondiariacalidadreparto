import streamlit as st
import pandas as pd
import plotly.express as px
import string

# Configuración de la página
st.set_page_config(page_title="Auditoría Logística Pro", layout="wide")

st.title("📦 Panel de Control Last Mile")
st.markdown("Carga tu reporte para analizar KPIs de repartidores y micro-hubs.")

# 1. Cargar Datos desde la Interfaz
archivo = st.sidebar.file_uploader("Sube tu archivo Excel", type=['xlsx', 'xls'])

if archivo:
    # Definir nombres de columnas (A, B, C...) como tenías en tu script
    column_names = list(string.ascii_uppercase[:17])
    
    # Leer el archivo correctamente
    df = pd.read_excel(archivo, names=column_names, header=0)
    
    # --- PROCESAMIENTO ---
    # Columna H = Repartidor | K = Estatus | L = Motivo | O = CP | M = Producto
    
    # 2. Análisis de Repartidores
    repartidor_counts = df['H'].value_counts().reset_index()
    repartidor_counts.columns = ['Repartidor', 'Total_Envios']
    
    # Filtro de efectividad (ajustado a tu lógica de 'Causa Ajena' o 'Efectividad')
    # Nota: Aquí puedes cambiar 'Causa Ajena' por el término que uses para entregado exitosas
    efectivos = df[df['L'].str.contains('entregado', na=False, case=False)]
    exitos_counts = efectivos['H'].value_counts().reset_index()
    exitos_counts.columns = ['Repartidor', 'Entregado_Exitosas']
    
    # Unir datos para el gráfico comparativo
    resumen_repartidores = pd.merge(repartidor_counts, exitos_counts, on='Repartidor', how='left').fillna(0)
    resumen_repartidores['Efectividad_%'] = (resumen_repartidores['entregado_Exitosas'] / resumen_repartidores['Total_Envios'] * 100).round(2)

    # --- VISUALIZACIÓN ---
    
    # Métricas Principales
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pedidos", len(df))
    col2.metric("Repartidores Activos", len(repartidor_counts))
    col3.metric("Efectividad Promedio", f"{resumen_repartidores['Efectividad_%'].mean():.1f}%")

    st.divider()

    # GRÁFICO COMPARATIVO (Lo que pediste)
    st.subheader("🏎️ Comparativa de Desempeño por Repartidor")
    fig_comp = px.bar(
        resumen_repartidores, 
        x='Repartidor', 
        y=['Total_Envios', 'Entregado_Exitosas'],
        barmode='group',
        color_discrete_map={'Total_Envios': '#636EFA', 'Entregado_Exitosas': '#00CC96'},
        title="Volumen vs Entregado Exitosas"
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # ANÁLISIS POR CÓDIGO POSTAL (Micro-hubs)
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.subheader("📍 Densidad por CP (Top 15)")
        cp_counts = df['O'].value_counts().head(15).reset_index()
        cp_counts.columns = ['CP', 'Envios']
        fig_cp = px.pie(cp_counts, values='Envios', names='CP', hole=0.4)
        st.plotly_chart(fig_cp, use_container_width=True)

    with col_der:
        st.subheader("⚠️ Incidencias por Repartidor")
        incidencias = df.groupby(['H', 'L']).size().reset_index(name='Cantidad')
        fig_inc = px.bar(incidencias.sort_values('Cantidad', ascending=False).head(10), 
                         x='Cantidad', y='H', color='L', orientation='h')
        st.plotly_chart(fig_inc, use_container_width=True)

    # Tabla de Detalle con Ranking
    st.subheader("📋 Ranking Detallado de Calidad")
    st.dataframe(resumen_repartidores.sort_values(by='Efectividad_%', ascending=False), use_container_width=True)

else:
    st.info
