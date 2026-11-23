import streamlit as st
import pandas as pd


@st.cache_data
def cargar_pedidos():
    return pd.read_csv("pedidos_limpios.csv")


@st.cache_data
def cargar_platos():
    return pd.read_csv("platos.csv")


st.set_page_config(page_title="La Consulta", page_icon="🍽️", layout="wide")
st.title("La Consulta a domicilio")
st.write("Análisis de los pedidos entregados entre septiembre y noviembre de 2026.")

pedidos = cargar_pedidos()
platos = cargar_platos()

with st.sidebar:
    st.header("Filtros")
    plataforma = st.selectbox("Plataforma", ["Todas"] + sorted(pedidos["plataforma"].unique().tolist()))
    barrio = st.selectbox("Barrio", ["Todos"] + sorted(pedidos["barrio"].unique().tolist()))

filtrados = pedidos.copy()
if plataforma != "Todas":
    filtrados = filtrados[filtrados["plataforma"] == plataforma]
if barrio != "Todos":
    filtrados = filtrados[filtrados["barrio"] == barrio]

if filtrados.empty:
    st.warning("No hay pedidos con esos filtros.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Pedidos", len(filtrados))
col2.metric("Neto medio", f"{filtrados['neto'].mean():.2f} €")
col3.metric("Minutos medios", f"{filtrados['minutos'].mean():.1f}")

pestañas = st.tabs(["Datos", "Gráficos", "Platos", "Tiempo de entrega"])

with pestañas[0]:
    st.dataframe(filtrados)

with pestañas[1]:
    pedidos_semana = filtrados.groupby("semana").size()
    st.line_chart(pedidos_semana)

    neto_plataforma = filtrados.groupby("plataforma")["neto"].mean()
    st.bar_chart(neto_plataforma)

with pestañas[2]:
    platos_sin_bebidas = platos[platos["categoria"] != "bebidas"].sort_values("unidades", ascending=False).head(10)
    st.bar_chart(platos_sin_bebidas.set_index("plato")["unidades"])

with pestañas[3]:
    barrio_elegido = st.selectbox("Elige el barrio", sorted(pedidos["barrio"].dropna().unique()))
    llueve = st.selectbox("¿Llueve?", ["No", "Sí"])
    grupo = pedidos[pedidos["barrio"] == barrio_elegido]
    if llueve == "Sí":
        grupo = grupo[grupo["llueve"]]
    else:
        grupo = grupo[~grupo["llueve"]]

    if grupo["minutos"].notna().any():
        st.success(f"Tiempo medio estimado: {grupo['minutos'].mean():.1f} minutos")
    else:
        st.info("No hay datos suficientes para esa combinación.")
