import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import string

# 1. Cargar Datos
column_names = list(string.ascii_uppercase[:17])
df = pd.read_excel('/st.file_uploader', names=column_names, header=0)

# 2. Análisis de Repartidores (Mayores/Menores Entregas)
effective_filter = 'Causa Ajena'
df_effective = df[df['K'] == effective_filter]
repartidor_counts = df_effective['H'].value_counts().reset_index()
repartidor_counts.columns = ['Repartidor', 'Frecuencia']
repartidor_counts['Porcentaje (%)'] = (repartidor_counts['Frecuencia'] / len(df) * 100).round(2)

top_5_max = repartidor_counts.head(5)
top_5_min = repartidor_counts.sort_values(by='Frecuencia', ascending=True).head(5)

# 3. Distribución por Código Postal
cp_counts = df['O'].value_counts().reset_index()
cp_counts.columns = ['Codigo_Postal', 'Envios']
cp_counts['Codigo_Postal'] = cp_counts['Codigo_Postal'].astype(str).str.replace('.0', '', regex=False)

# 4. Producto Dominante por CP
dominant_products_df = df.groupby(['O', 'M']).size().reset_index(name='Cantidad')
dominant_products_df['Codigo_Postal'] = dominant_products_df['O'].astype(str).str.replace('.0', '', regex=False)
dominant_per_cp = dominant_products_df.sort_values(['Codigo_Postal', 'Cantidad'], ascending=[True, False]).drop_duplicates(subset='Codigo_Postal')

# 5. Estrategia Micro-Hubs
hub_data = cp_counts.head(15).copy()
hub_data['Prefijo'] = hub_data['Codigo_Postal'].str[:3]
micro_hubs = hub_data.loc[hub_data.groupby('Prefijo')['Envios'].idxmax()]

# 6. Consolidación de Incidencias
incidencias_por_repartidor = df.groupby(['H', 'L']).size().reset_index(name='Cantidad_Incidencias').sort_values(by='Cantidad_Incidencias', ascending=False)

print('Script de análisis generado exitosamente.')
