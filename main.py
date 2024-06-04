#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import math
import pulp
from google.cloud import bigquery
import os


# In[2]:


def Query_1(Llave):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Llave
    client = bigquery.Client()
    sql = """
    SELECT transaction_id,latitud_pedido,longitud_pedido,ventaneta_ecommercedelivery
    FROM inretail-negocios-sd.intercorpretail_temp.base_transaccionesecommercedelivery_2023_v3 A
    WHERE latitud_pedido IS NOT NULL
    LIMIT 100
    """
    Ventas_Anho_Operacion = client.query(sql).to_dataframe()
    return Ventas_Anho_Operacion 


def Query_2(Llave):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Llave
    client = bigquery.Client()
    sql = """
    SELECT A.place_id,A.place_description,latitud,longitud
    FROM inretail-negocios-sd.intercorpretail_temp.base_transaccionesecommercedelivery_2023_v3 A
    LEFT JOIN `inretail-negocios-sd.intercorpretail_tablas_maestras.m_place_inretail` B ON A.place_id = B.place_id
    GROUP BY A.place_id,A.place_description,latitud,longitud
    """
    Ventas_Anho_Operacion = client.query(sql).to_dataframe()
    return Ventas_Anho_Operacion 


# In[3]:


Ruta_Inicial=os.getcwd()
Ruta_Inicial


# In[4]:


os.chdir(Ruta_Inicial)
ruta=Ruta_Inicial.replace("\\","/")
Llave=[s for s in os.listdir(ruta) if any(xs in s for xs in ['inretail-negocios-sd-d971f65571f5'])][0]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Llave
client = bigquery.Client()


# In[5]:


Query_1(Llave)


# In[6]:


locales_df = Query_2(Llave)
pedidos_df = Query_1(Llave)


# In[7]:


# Verificar la lectura y filtración de datos
print(locales_df.head())
print(pedidos_df.head())


# In[8]:


def calcular_distancia(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)


# In[9]:


# Definir un diccionario para almacenar las distancias
cobertura = {}

for i, local in locales_df.iterrows():
    for j, pedido in pedidos_df.iterrows():
        dist = calcular_distancia(local['latitud'], local['longitud'], pedido['latitud_pedido'], pedido['longitud_pedido'])
        cobertura[(local['place_description'], pedido['transaction_id'])] = dist


# In[10]:


# Imprimir algunas distancias calculadas para verificar
for key, value in list(cobertura.items())[:5]:
    print(f"Distancia entre {key[0]} y {key[1]}: {value}")


# In[11]:


# Crear el modelo de optimización
modelo = pulp.LpProblem("Minimo_Numero_de_Locales", pulp.LpMinimize)


# In[12]:


# Definir variables de decisión
x = pulp.LpVariable.dicts("x", locales_df['place_description'], 0, 1, pulp.LpBinary)
y = pulp.LpVariable.dicts("y", [(local, pedido) for local in locales_df['place_description'] for pedido in pedidos_df['transaction_id']], 0, 1, pulp.LpBinary)


# In[13]:


# Definir la función objetivo
modelo += pulp.lpSum(x[local] for local in locales_df['place_description']), "Numero_Locales"

# Restricciones para asegurar que cada pedido es atendido por al menos un local
for pedido in pedidos_df['transaction_id']:
    modelo += pulp.lpSum(y[(local, pedido)] for local in locales_df['place_description']) >= 1, f"Pedido_{pedido}"
# Restricciones para asegurar que un pedido solo puede ser atendido por un local si ese local está abierto
for local in locales_df['place_description']:
    for pedido in pedidos_df['transaction_id']:
        modelo += y[(local, pedido)] <= x[local], f"Asig_{local}_{pedido}"

# Resolver el problema
modelo.solve()

# Imprimir resultados
for v in modelo.variables():
    if v.varValue > 0:
        print(f"{v.name} = {v.varValue}")

print(f"Numero Total de Locales Abiertos: {pulp.value(modelo.objective)}")


# In[ ]:




