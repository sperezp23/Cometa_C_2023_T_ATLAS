# %% Librerías
import requests
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from astroquery.mpc import MPC

# %% Funciones  

# Verificar la conexión a internet.
def verificar_conexion():
    try:
        requests.get("http://www.google.com", timeout=5)
        print('✅ Conectado a internet.')
        print('✅ Conectando con la base de datos.')
        return True
    
    except requests.ConnectionError:
        print('🛑 Sin conexión a internet.')
        return False
    
# %%  Conexión con la API de COBS
nombre_cometa = input('Ingrese el nombre del cometa:\n') #'C/2023 A3' 

Link_cops_API = f'https://cobs.si/api/obs_list.api?des={nombre_cometa}&format=json&from_date=&to_date=&exclude_faint=False&exclude_not_accurate=False'

if verificar_conexion():
    response = requests.get(Link_cops_API)

if response.status_code == 200:
    content = response.json()
    print('✅ Base de datos actualizada.')

else:
    print(f'🛑 Se presentó un error al cargar la base de datos.\nError: {response.status_code}\n{response.content}')

# %% Creación del data frame Cometa
cometa_df = pd.DataFrame(content['objects'])


# %% Tratamiento de los datos de interés
cometa_df['obs_method_key'] = cometa_df.obs_method.apply(lambda registro: registro['key'])
cometa_df['obs_date'] = pd.to_datetime(pd.to_datetime(cometa_df.obs_date).dt.date)
cometa_df['magnitude'] = pd.to_numeric(cometa_df.magnitude)

# %%  Creación del data frame curva de luz cruda
curva_de_luz_cruda_df = cometa_df[['obs_method_key', 'obs_date', 'magnitude']].copy()

# %%  Curva de luz cruda.
labels = {'obs_date':'Observation Date','magnitude':'Apparent total magnitude', 'obs_method_key' : 'Observation Method'}
fig = px.scatter(curva_de_luz_cruda_df, x='obs_date', y='magnitude', color='obs_method_key', template= 'plotly_dark', labels= labels, title='Lightcurve of comet C/2023 A3 (Tsuchinshan-ATLAS)')
fig.update_yaxes(autorange="reversed")
fig.show()
print('✅ Curva de luz cruda creada.')

# %%  Creación de data frame Ephemeris (conexión con la API del MPC)
fecha_inicial = curva_de_luz_cruda_df.obs_date.min()
fecha_final = curva_de_luz_cruda_df.obs_date.max()
fechas = (fecha_final - fecha_inicial).days + 1 if (fecha_final - fecha_inicial).days <= 1441 else 1441

ephemeris = MPC.get_ephemeris(nombre_cometa, start = str(fecha_inicial), number = fechas) # type: ignore

ephemeris_df = ephemeris.to_pandas()
ephemeris_df.columns = ephemeris_df.columns.str.lower().str.replace(' ', '_')
# %% Creación del data frame ephemeris filtrada
ephemeris_filtrada_df = ephemeris_df[['date', 'delta','r', 'phase']].copy()
ephemeris_filtrada_df = ephemeris_filtrada_df.rename(columns = {'date':'obs_date'})

# %% Unión de las bases de datos COBS y MPC
curva_de_luz_procesada_df = curva_de_luz_cruda_df.merge(ephemeris_filtrada_df, on='obs_date')

# Reducción de la magnitud aparente
beta = 0

curva_de_luz_procesada_df['magnitud_reducida'] = (
    curva_de_luz_cruda_df['magnitude'] 
    - 5 * np.log10(curva_de_luz_procesada_df['delta'] * curva_de_luz_procesada_df['r'])
    - (beta * curva_de_luz_procesada_df['phase'])
    )

# %% Curva de luz reducida
labels = {'obs_date':'Observation Date','magnitud_reducida':'Apparent total magnitude processed', 'obs_method_key' : 'Observation Method'}
fig = px.scatter(curva_de_luz_procesada_df, x='obs_date', y='magnitud_reducida', color='obs_method_key', template= 'plotly_dark', labels= labels, title=f'Reduced Lightcurve of comet {nombre_cometa} (Tsuchinshan-ATLAS)')
fig.update_yaxes(autorange="reversed")
fig.show()
print('✅ Curva de luz reducida creada.')

# %% Creación del data frame curva de luz agrupada
curva_de_luz_externa_df = curva_de_luz_procesada_df.groupby(by = 'obs_date').min()
curva_de_luz_externa_df = curva_de_luz_externa_df.reset_index()

# %%  Creación del data frame curva de luz promediada
numero_elementos_grupo = 7

curva_de_luz_externa_df = curva_de_luz_externa_df.copy()
curva_de_luz_externa_df['promedio_movil'] = curva_de_luz_externa_df.magnitud_reducida.rolling(window = numero_elementos_grupo).mean()

# %% Curva de luz reducida
labels = {'obs_date':'Observation Date','magnitud_reducida':'Max apparent total magnitude reduced', 'obs_method_key' : 'Observation Method'}
fig = px.scatter(curva_de_luz_externa_df, x=curva_de_luz_externa_df.obs_date, y='magnitud_reducida', color='obs_method_key', template= 'plotly_dark', labels= labels, title=f'Max Lightcurve of comet {nombre_cometa} (Tsuchinshan-ATLAS)')
fig.update_yaxes(autorange="reversed")
fig.show()
print('✅ Maxima curva de luz reducida creada.')

# %%  Gráfica de luz promediada
labels = {'obs_date':'Observation Date','magnitud_reducida':'Magnitude reduced'}
fig = px.scatter(curva_de_luz_externa_df, x=curva_de_luz_externa_df.obs_date, y='promedio_movil', template= 'plotly_dark', labels= labels, title=f'Max Averaged Lightcurve of comet {nombre_cometa} (Tsuchinshan-ATLAS)')
fig.update_traces(marker=dict(color='yellow', size=6, line=dict(width=1, color='DarkSlateGrey')))
fig.update_yaxes(autorange="reversed")
fig.show()
print('✅ Curva de luz promediada.')