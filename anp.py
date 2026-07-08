"""
==========================================================
ANP.PY
Método ANP - Analytic Network Process
Universidad Central del Ecuador

Autor: Abigail Quilumba

Este archivo contiene todas las funciones matemáticas
utilizadas por la aplicación principal.

==========================================================
"""

import numpy as np
import pandas as pd

# ==========================================================
# ÍNDICES ALEATORIOS DE SAATY
# ==========================================================

RI = {
    1:0.00,
    2:0.00,
    3:0.58,
    4:0.90,
    5:1.12,
    6:1.24,
    7:1.32,
    8:1.41,
    9:1.45,
    10:1.49
}

# ==========================================================
# CREAR MATRIZ DE SAATY
# ==========================================================

def crear_matriz(n):
    """
    Crea una matriz identidad de tamaño n.
    """

    return np.eye(n)

# ==========================================================
# LLENAR MATRIZ
# ==========================================================

def llenar_matriz(matriz, comparaciones):

    """
    Construye automáticamente la matriz de Saaty.

    Parámetros
    ----------
    matriz : ndarray
    comparaciones : lista de comparaciones

    Retorna
    -------
    matriz completa
    """

    n = len(matriz)

    indice = 0

    for i in range(n):

        for j in range(i+1,n):

            valor = comparaciones[indice]

            matriz[i,j]=valor

            matriz[j,i]=1/valor

            indice += 1

    return matriz

# ==========================================================
# SUMA DE COLUMNAS
# ==========================================================

def suma_columnas(matriz):

    """
    Calcula la suma de cada columna.
    """

    return matriz.sum(axis=0)

# ==========================================================
# MATRIZ NORMALIZADA
# ==========================================================

def normalizar_matriz(matriz):

    """
    Divide cada elemento por la suma de su columna.
    """

    suma = suma_columnas(matriz)

    matriz_normalizada = matriz / suma

    return matriz_normalizada

# ==========================================================
# VECTOR DE PRIORIDADES
# ==========================================================

def vector_prioridades(matriz_normalizada):

    """
    Calcula el promedio de cada fila.
    """

    return matriz_normalizada.mean(axis=1)

# ==========================================================
# CALCULAR λ MAX
# ==========================================================

def lambda_max(matriz, prioridades):

    """
    Calcula el valor propio máximo.
    """

    producto = np.dot(matriz, prioridades)

    cociente = producto / prioridades

    return np.mean(cociente)

# ==========================================================
# ÍNDICE DE CONSISTENCIA
# ==========================================================

def indice_consistencia(lambda_maximo,n):

    """
    Calcula el CI.
    """

    return (lambda_maximo-n)/(n-1)

# ==========================================================
# RAZÓN DE CONSISTENCIA
# ==========================================================

def razon_consistencia(ci,n):

    """
    Calcula el CR.
    """

    if n<=2:

        return 0

    return ci/RI[n]

# ==========================================================
# VALIDAR CONSISTENCIA
# ==========================================================

def validar_consistencia(cr):

    """
    Devuelve True si la matriz es consistente.
    """

    if cr<=0.10:

        return True

    return False

# ==========================================================
# MOSTRAR RESULTADOS
# ==========================================================

def resumen_resultados(matriz):

    """
    Calcula automáticamente todos los resultados.
    """

    normalizada = normalizar_matriz(matriz)

    prioridades = vector_prioridades(normalizada)

    lm = lambda_max(matriz, prioridades)

    ci = indice_consistencia(lm,len(matriz))

    cr = razon_consistencia(ci,len(matriz))

    return {

        "matriz":matriz,

        "normalizada":normalizada,

        "prioridades":prioridades,

        "lambda":lm,

        "ci":ci,

        "cr":cr,

        "consistente":validar_consistencia(cr)

    }

# ==========================================================
# CONSTRUCCIÓN DE LA RED ANP
# ==========================================================

def crear_matriz_dependencias(criterios):
    """
    Crea una matriz vacía de dependencias entre criterios.
    """

    n = len(criterios)

    matriz = np.zeros((n, n))

    return pd.DataFrame(
        matriz,
        index=criterios,
        columns=criterios
    )


# ==========================================================
# REGISTRAR DEPENDENCIA
# ==========================================================

def registrar_dependencia(matriz, origen, destino, peso):
    """
    Registra la influencia de un criterio sobre otro.
    """

    matriz.loc[origen, destino] = peso

    return matriz


# ==========================================================
# NORMALIZAR MATRIZ DE DEPENDENCIAS
# ==========================================================

def normalizar_dependencias(matriz):
    """
    Normaliza cada columna de la matriz de dependencias.
    """

    matriz = matriz.copy()

    for columna in matriz.columns:

        suma = matriz[columna].sum()

        if suma > 0:

            matriz[columna] = matriz[columna] / suma

    return matriz


# ==========================================================
# SUPERMATRIZ
# ==========================================================

def construir_supermatriz(prioridades, dependencias):
    """
    Construye la supermatriz ANP.
    """

    n = len(prioridades)

    supermatriz = np.zeros((n, n))

    for i in range(n):

        for j in range(n):

            supermatriz[i, j] = prioridades[i] * dependencias.iloc[i, j]

    return pd.DataFrame(
        supermatriz,
        index=dependencias.index,
        columns=dependencias.columns
    )

# ==========================================================
# SUPERMATRIZ PONDERADA
# ==========================================================

def supermatriz_ponderada(supermatriz):
    """
    Normaliza la supermatriz.
    """

    matriz = supermatriz.copy()

    for columna in matriz.columns:

        suma = matriz[columna].sum()

        if suma > 0:

            matriz[columna] = matriz[columna] / suma

    return matriz

# ==========================================================
# SUPERMATRIZ LÍMITE
# ==========================================================

def supermatriz_limite(supermatriz, iteraciones=50):
    """
    Calcula la supermatriz límite.
    """

    matriz = supermatriz.values.copy()

    for _ in range(iteraciones):

        matriz = np.dot(matriz, matriz)

    return pd.DataFrame(
        matriz,
        index=supermatriz.index,
        columns=supermatriz.columns
    )
