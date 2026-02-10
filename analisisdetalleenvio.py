import streamlit as st
import pandas as pd
import plotly.express as px
import string

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Auditoría Logística Pro", layout="wide")

st.title("📦 Panel de Control: Entregado vs Efectividad")
st.markdown("Esta versión busca automáticamente tanto 'Entregado' como 'Efectividad' para no perder datos.")

# --- 1. CARGA DE DATOS ---
archivo = st.sidebar.file_uploader("Sube tu reporte Excel (.xlsx)", type=['xlsx'])

if archivo:
    # Definimos nombres de columnas estándar (A-Q)
    column_names = list(string.ascii_uppercase[:17])
    
    try:
        df = pd.read_excel(archivo, names=column_names, header=0)
        
        # --- 2. PROCESAMIENTO CON DOBLE VALIDACIÓN ---
        # H=Repartidor | L=Estado | O=CP
        
        # Conteo total de envíos por repartidor
        repartidor_counts = df['H'].value_counts().reset_index()
        repartidor_counts.columns = ['Repartidor', 'Total_Envios']
        
        # LÓGICA CLAVE: Filtramos si contiene 'entregado' O 'efectividad'
        # Usamos el operador '|' que significa "O" en programación
        condicion_exito = (
            df['L'].astype(str).str.contains('entregado', na=False, case=False) | 
            df['L'].astype(str).str.contains('efectividad', na=False, case=False)
        )
        
        efectivos = df[condicion_exito]
        
        exitos_counts = efectivos['H'].value_counts().reset_index()
        exitos_counts.columns = ['Repartidor', 'Entregas_Exitosas']
        
        # Unión de datos
        resumen_repartidores = pd.merge(repartidor_counts, exitos_counts, on='Repartidor', how='left').fillna(0)
        
        # Cálculo de Efectividad %
        resumen_repartidores['Efectividad_%'] = (resumen_repartidores['Entregas_Exitosas'] / resumen_repartidores['Total_Envios'] * 100).round(2)
        
        # --- 3. VISUALIZACIÓN ---
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Pedidos", len(df))
        m2.metric("Éxitos (Entregado/Efectividad)", int(resumen_repartidores['Entregas_Exitosas'].sum()))
        m3.metric("Efectividad Global", f"{resumen_repartidores['Efectividad_%'].mean():.1f}%")
        
        st.divider()
        
        # Gráfico de Desempeño
        st.subheader("🏎️ Comparativa de Repartidores")
        fig_repa = px.bar(
            resumen_repartidores.sort_values('Total_Envios', ascending=False), 
            x='Repartidor', 
            y=['Total_Envios', 'Entregas_Exitosas'],
            barmode='group',
            color_discrete_map={'Total_Envios': '#3498db', 'Entregas_Exitosas': '#2ecc71'},
            text_auto='.2s'
        )
        st.plotly_chart(fig_repa, use_container_width=True)

        # Tabla de Ranking
        st.subheader("📋 Ranking de Calidad")
        st.dataframe(resumen_repartidores.sort_values('Efectividad_%', ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"Error técnico: {e}")
else:
    st.info("👋 Esperando archivo Excel...")
