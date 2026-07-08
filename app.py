# ===============================
# IMPORTAR LIBRERÍAS
# ===============================

import streamlit as st
import pandas as pd
import numpy as np
# ============================================
# ============================================
# IMPORTAR FUNCIONES DEL MÉTODO ANP
# ============================================
from anp import (
    crear_matriz,
    llenar_matriz,
    resumen_resultados,
    crear_matriz_dependencias,
    normalizar_dependencias,
    construir_supermatriz,
    supermatriz_ponderada,
    supermatriz_limite
)

# ===============================
# CONFIGURACIÓN DE LA PÁGINA
# ===============================

st.set_page_config(
    page_title="Sistema ANP",
    layout="wide"
)

# ===============================
# ESTILOS
# ===============================

st.markdown("""
<style>

.stApp{
    background:#F4F8FB;
}

h1{
    color:#0B5394;
    text-align:center;
}

h2{
    color:#1F77B4;
}

h3{
    color:#1F77B4;
}

div[data-testid="stButton"] button{
    background:#1976D2;
    color:white;
    border-radius:10px;
    height:50px;
    width:220px;
    font-size:18px;
}

</style>
""", unsafe_allow_html=True)

# ===============================
# SIDEBAR
# ===============================

st.sidebar.title("Menú")

st.sidebar.success("Método ANP")

st.sidebar.markdown("---")

st.sidebar.write("Pasos del sistema")

st.sidebar.write("1️.Cargar Base")

st.sidebar.write("2️. Alternativas")

st.sidebar.write("3️. Criterios")

st.sidebar.write("4️. Costo / Beneficio")

st.sidebar.write("5️. Comparaciones")

st.sidebar.write("6️. Resultados")

# ===============================
# TÍTULO
# ===============================

st.title("Sistema de Apoyo a la Decisión")

st.subheader("Método ANP (Analytic Network Process)")

st.markdown("---")

st.info("""
Esta aplicación permite resolver problemas de decisión multicriterio mediante el método ANP.

El usuario será guiado paso a paso.
""")

# ===============================
# PROBLEMA
# ===============================

st.header("1️. Definición del problema")

problema = st.text_input(
    "Ingrese el nombre del problema"
)

st.markdown("---")

# ===============================
# CARGAR BASE
# ===============================

st.header("2️. Cargar Base de Datos")

archivo = st.file_uploader(

    "Seleccione un archivo",

    type=["csv","xlsx"]

)

# ===============================
# LEER ARCHIVO
# ===============================

if archivo is not None:

    try:

        if archivo.name.endswith(".csv"):

            try:

                df = pd.read_csv(

                    archivo,

                    sep=None,

                    engine="python",

                    encoding="utf-8",

                    on_bad_lines="skip"

                )

            except:

                archivo.seek(0)

                try:

                    df = pd.read_csv(

                        archivo,

                        sep=";",

                        encoding="latin1",

                        on_bad_lines="skip"

                    )

                except:

                    archivo.seek(0)

                    df = pd.read_csv(

                        archivo,

                        sep=",",

                        encoding="latin1",

                        on_bad_lines="skip"

                    )

        else:

            df = pd.read_excel(archivo)

        st.success("Base cargada correctamente")

        st.write("")

        st.subheader("Vista previa")

        st.dataframe(df.head(10), use_container_width=True)

        st.write("")

        c1,c2,c3 = st.columns(3)

        c1.metric("Filas",df.shape[0])

        c2.metric("Columnas",df.shape[1])

        c3.metric("Variables",len(df.columns))

    except Exception as e:

        st.error("No fue posible leer la base.")

        st.exception(e)

else:

    st.warning("Seleccione un archivo.")




# ============================================================
# SELECCIÓN DE ALTERNATIVAS Y CRITERIOS
# ============================================================

if archivo is not None:

    st.markdown("---")

    st.header("3️. Selección de Alternativas")

    alternativa = st.selectbox(
        "Seleccione la columna que representa las alternativas",
        df.columns
    )

    st.success(f"Alternativa seleccionada: {alternativa}")

    st.markdown("---")

    st.header("4️. Selección de Criterios")

    columnas_numericas = list(df.select_dtypes(include=np.number).columns)

    criterios = st.multiselect(
        "Seleccione los criterios de evaluación",
        [c for c in columnas_numericas if c != alternativa]
    )

    if len(criterios) >= 2:

        st.success(f"Se seleccionaron {len(criterios)} criterios.")

        st.markdown("---")

        st.header("5️. Tipo de criterio")

        tipos = {}

        for criterio in criterios:

            tipos[criterio] = st.radio(
                f"{criterio}",
                ["Beneficio", "Costo"],
                horizontal=True,
                key=f"tipo_{criterio}"
            )

        st.markdown("---")

        st.header("6️. Resumen del problema")

        resumen = pd.DataFrame({
            "Criterio": criterios,
            "Tipo": [tipos[c] for c in criterios]
        })

        st.dataframe(resumen, use_container_width=True)

        st.success("La información se registró correctamente.")

        if st.button("Continuar al método ANP"):

            st.session_state["problema"] = problema
            st.session_state["alternativa"] = alternativa
            st.session_state["criterios"] = criterios
            st.session_state["tipos"] = tipos

            st.success("Información guardada correctamente.")

            st.info("En el siguiente paso construiremos automáticamente la matriz de comparaciones de Saaty.")

    else:

        st.warning("Seleccione al menos dos criterios.")


# ============================================================
# BLOQUE 3.1
# COMPARACIONES POR PARES (ESCALA DE SAATY)
# ============================================================

import itertools

# Verificamos que ya se haya guardado la información
if "criterios" in st.session_state:

    st.markdown("---")
    st.header("7️. Comparaciones por Pares (Escala de Saaty)")

    st.write("""
    Compare la importancia relativa entre cada par de criterios utilizando
    la escala de Saaty.
    """)

    criterios = st.session_state["criterios"]

    comparaciones = {}

    # Generar automáticamente todas las combinaciones de criterios
    pares = list(itertools.combinations(criterios, 2))

    for criterio1, criterio2 in pares:

        st.subheader(f"{criterio1}  vs  {criterio2}")

        comparaciones[(criterio1, criterio2)] = st.select_slider(

            f"Seleccione la importancia",

            options=[
                1,2,3,4,5,6,7,8,9
            ],

            value=1,

            key=f"{criterio1}_{criterio2}"

        )

        st.caption("""
1 = Igual importancia

3 = Importancia moderada

5 = Importancia fuerte

7 = Importancia muy fuerte

9 = Importancia extrema
""")
if st.button("Construir Matriz de Comparación"):

    # ==========================================
    # CONSTRUIR MATRIZ DE SAATY
    # ==========================================

    valores = []

    for par in pares:
        valores.append(comparaciones[par])

    matriz = crear_matriz(len(criterios))

    matriz = llenar_matriz(matriz, valores)

    resultados = resumen_resultados(matriz)

    st.session_state["matriz"] = matriz

    st.markdown("---")

    st.subheader("Matriz de Comparación")

    st.dataframe(
        pd.DataFrame(
            resultados["matriz"],
            index=criterios,
            columns=criterios
        ).style.format("{:.3f}"),
        use_container_width=True
    )

    st.subheader("Matriz Normalizada")

    st.dataframe(
        pd.DataFrame(
            resultados["normalizada"],
            index=criterios,
            columns=criterios
        ).style.format("{:.4f}"),
        use_container_width=True
    )

    st.subheader("Vector de Prioridades")

    prioridades = pd.DataFrame({
        "Criterio": criterios,
        "Peso": resultados["prioridades"]
    })

    st.dataframe(
        prioridades.style.format({
            "Peso": "{:.4f}"
        }),
        use_container_width=True
    )

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "λ Máximo",
        round(resultados["lambda"], 4)
    )

    c2.metric(
        "CI",
        round(resultados["ci"], 4)
    )

    c3.metric(
        "CR",
        round(resultados["cr"], 4)
    )

    if resultados["consistente"]:
        st.success("La matriz es consistente (CR ≤ 0.10)")
    else:
        st.error("La matriz NO es consistente (CR > 0.10)")
        st.warning("Debe repetir las comparaciones.")



    # ==========================================
    # BLOQUE 5
    # RANKING DE CRITERIOS
    # ==========================================

    st.markdown("---")
    st.header("Ranking de Prioridades")

    ranking = pd.DataFrame({
        "Criterio": criterios,
        "Peso": resultados["prioridades"]
    })

    ranking = ranking.sort_values(
        by="Peso",
        ascending=False
    )

    ranking["Posición"] = range(1, len(ranking) + 1)

    ranking = ranking[
        ["Posición", "Criterio", "Peso"]
    ]

    st.dataframe(
        ranking.style.format({
            "Peso": "{:.4f}"
        }),
        use_container_width=True
    )

    st.session_state["ranking"] = ranking



    # ==========================================
    # GRÁFICO DEL RANKING
    # ==========================================

    st.subheader("Importancia de los Criterios")

    grafico = ranking.set_index("Criterio")

    st.bar_chart(
        grafico["Peso"]
    )


    # ==========================================
    # RESUMEN FINAL
    # ==========================================

    st.markdown("---")

    st.success("Método ejecutado correctamente.")

    st.write("Resumen:")

    st.write(f"• λ Máximo: {resultados['lambda']:.4f}")

    st.write(f"• Índice de Consistencia (CI): {resultados['ci']:.4f}")

    st.write(f"• Razón de Consistencia (CR): {resultados['cr']:.4f}")

    if resultados["consistente"]:

        st.success("La matriz cumple el criterio de consistencia.")

    else:

        st.error("La matriz NO cumple el criterio de consistencia.")


# ============================================================
# BLOQUE 8: CONFIGURACIÓN DE DEPENDENCIAS (ANP)
# ============================================================
# Solo mostramos esto si ya pasamos por los pasos anteriores
if "ranking" in st.session_state:
    st.markdown("---")
    st.header("8️. Configurar Dependencias (ANP)")
    st.write("Defina cómo influye cada criterio sobre los otros (Valores de 0 a 1).")

    # Obtenemos los criterios guardados anteriormente
    criterios = st.session_state["criterios"]
    
    # Creamos la matriz
    df_deps = crear_matriz_dependencias(criterios)
    matriz_editada = st.data_editor(df_deps, key="editor_deps")

    if st.button("Calcular Resultados ANP Finales"):
        # Extraer pesos calculados en el bloque de AHP
        prioridades_vector = st.session_state["ranking"]["Peso"].values
        
        # Procesamiento ANP
        matriz_norm = normalizar_dependencias(matriz_editada)
        super_m = construir_supermatriz(prioridades_vector, matriz_norm)
        super_p = supermatriz_ponderada(super_m)
        resultado_anp = supermatriz_limite(super_p)
        
        # Mostrar resultado final
        st.subheader("Ranking Final (Estabilizado por ANP)")
        st.dataframe(resultado_anp, use_container_width=True)
        
        st.success("¡El proceso de red (ANP) ha finalizado correctamente!")