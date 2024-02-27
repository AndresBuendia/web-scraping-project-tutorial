#!pip install pandas requests beautifulsoup4
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup

# Realizar la solicitud HTTP
url = 'https://stockanalysis.com/stocks/tsla/revenue/'
response = requests.get(url)

# Verificar si la solicitud fue exitosa
print(f"Estado de la respuesta: {response.status_code}")

if response.status_code == 200:
    html_content = response.text

    # Parsear el contenido HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Intentar encontrar la tabla con la clase específica
    table = soup.find('table', {'class': 'svelte-1jtwn20'})

    # Verificar si se encontró la tabla
    if table:
        print("Tabla encontrada. Extrayendo datos...")
        
        # Inicializar una lista para almacenar todos los datos de la tabla
        data = []
        
        # Extraer las filas de la tabla
        rows = table.find_all('tr')
        
        # Extraer las cabeceras de la tabla
        headers = [header.get_text() for header in rows[0].find_all('th')]
        data.append(headers)
        
        # Extraer el contenido de cada fila
        for row in rows[1:]:  # Saltar la cabecera
            values = [value.get_text() for value in row.find_all('td')]
            data.append(values)
        
        # Imprimir los datos extraídos
        for row in data:
            print(row)
    else:
        print("No se encontró una tabla con la clase especificada.")
else:
    print(f"Error al realizar la solicitud HTTP: {response.status_code}")

# Ahora convertimos la lista de datos en un DataFrame de Pandas
df = pd.DataFrame(data[1:], columns=[col.strip() for col in data[0]])

# Imprimimos los nombres de las columnas para verificar
print(df.columns)

def convert_to_number(x):
    if x == '-':  # Verifica si el valor es un guión y lo reemplaza por 0
        return 0.0
    if 'B' in x:
        return float(x.replace('B', '')) * 1e9
    elif 'M' in x:
        return float(x.replace('M', '')) * 1e6
    elif 'K' in x:
        return float(x.replace('K', '')) * 1e3
    else:
        return float(x)

df['Revenue'] = df['Revenue'].str.replace(',', '').apply(convert_to_number)
df['Change'] = df['Change'].str.replace(',', '').apply(convert_to_number)


# Para 'Growth', eliminamos tanto las comas como el símbolo de porcentaje antes de la conversión
df['Growth'] = df['Growth'].str.replace(',', '').str.rstrip('%').replace('-', '0').astype(float) / 100

# Imprimimos el DataFrame resultante para verificar
print(df)


# Configurar estilo de Seaborn
sns.set(style="whitegrid")

# Convertir 'Fiscal Year End' a datetime para facilitar la visualización
df['Fiscal Year End'] = pd.to_datetime(df['Fiscal Year End'])

# 1. Tendencia de ingresos a lo largo de los años
plt.figure(figsize=(10, 6))
sns.lineplot(x='Fiscal Year End', y='Revenue', data=df, marker='o')
plt.title('Tendencia de Ingresos de Tesla (2007-2023)')
plt.xlabel('Año')
plt.ylabel('Ingresos (en miles de millones)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 2. Tasa de crecimiento año tras año
plt.figure(figsize=(10, 6))
sns.lineplot(x='Fiscal Year End', y='Growth', data=df, marker='o', color='orange')
plt.title('Tasa de Crecimiento Anual de Tesla (2007-2023)')
plt.xlabel('Año')
plt.ylabel('Tasa de Crecimiento')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 3. Cambios anuales en los ingresos
plt.figure(figsize=(10, 6))
sns.barplot(x='Fiscal Year End', y='Change', data=df, palette='viridis')
plt.title('Cambios Anuales en los Ingresos de Tesla (2007-2023)')
plt.xlabel('Año')
plt.ylabel('Cambio en los Ingresos (en miles de millones)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()