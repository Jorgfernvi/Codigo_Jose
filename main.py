#!/usr/bin/env python
# coding: utf-8

# In[9]:


import pandas as pd
import math
import pulp


# In[6]:


locales_df = pd.read_csv("base_localesdelivery.csv")
pedidos_df = pd.read_csv("base_transaccionesecommercedelivery_2023.csv",usecols=['transaction_id','latitud_pedido','longitud_pedido']).dropna(subset=['latitud_pedido'])


# In[8]:


# Verificar la lectura y filtración de datos
print(locales_df.head())
print(pedidos_df.head())


# In[10]:


def calcular_distancia(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)


# In[13]:


# Definir un diccionario para almacenar las distancias
cobertura = {}

for i, local in locales_df.iterrows():
    for j, pedido in pedidos_df.iterrows():
        dist = calcular_distancia(local['latitud'], local['longitud'], pedido['latitud_pedido'], pedido['longitud_pedido'])
        cobertura[(local['place_description'], pedido['transaction_id'])] = dist


# In[15]:


# Imprimir algunas distancias calculadas para verificar
for key, value in list(cobertura.items())[:5]:
    print(f"Distancia entre {key[0]} y {key[1]}: {value}")


# In[16]:


# Crear el modelo de optimización
modelo = pulp.LpProblem("Minimo_Numero_de_Locales", pulp.LpMinimize)


# In[17]:


# Definir variables de decisión
x = pulp.LpVariable.dicts("x", locales_df['place_description'], 0, 1, pulp.LpBinary)
y = pulp.LpVariable.dicts("y", [(local, pedido) for local in locales_df['place_description'] for pedido in pedidos_df['transaction_id']], 0, 1, pulp.LpBinary)


# In[18]:


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




