import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import streamlit as st
import plotly.express as px

load_dotenv()

def conectar_banco():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@st.cache_data
def carregar_dados():
    conn = conectar_banco()
    query = """
        SELECT j.nome, t.nome AS time, e.gols, e.assistencias,
               (e.gols + e.assistencias) AS ga
        FROM jogadores j
        JOIN times t ON j.time_id = t.id
        JOIN estatisticas e ON j.id = e.jogador_id;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.set_page_config(
    page_title="Dashboard de Futebol",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚽"
)

with st.sidebar:
    st.header("Controles")
    if st.button("Recarregar Dados"):
        st.cache_data.clear()
    st.markdown("---")
    st.markdown("Filtro de Time")
    df_full = carregar_dados()
    times = ["Todos"] + df_full["time"].unique().tolist()
    filtro_time = st.selectbox("Selecione um time", times)
    st.markdown("---")

df = df_full if filtro_time == "Todos" else df_full[df_full["time"] == filtro_time]

k1, k2, k3 = st.columns(3)
k1.metric("Gols Totais", int(df["gols"].sum()))
k2.metric("Assistências Totais", int(df["assistencias"].sum()))
k3.metric("Jogadores", int(df["nome"].nunique()))

st.markdown("")

soft_palette = px.colors.qualitative.Prism

with st.container():
    st.subheader("Top 5 Artilheiros")
    top_gols = df.nlargest(5, "gols")
    fig1 = px.bar(
        top_gols, x="nome", y="gols", color="time",
        text_auto=True, template="plotly_white",
        color_discrete_sequence=soft_palette
    )
    st.plotly_chart(fig1, use_container_width=True)

with st.container():
    st.subheader("Top 5 Gols + Assistências (G+A)")
    top_ga = df.nlargest(5, "ga")
    fig2 = px.bar(
        top_ga, x="nome", y="ga", color="time",
        text_auto=True, template="plotly_white",
        color_discrete_sequence=soft_palette
    )
    st.plotly_chart(fig2, use_container_width=True)

with st.container():
    st.subheader("Distribuição de Gols por Time")
    gols_por_time = df.groupby("time", as_index=False)["gols"].sum()
    fig3 = px.pie(
        gols_por_time, names="time", values="gols",
        template="plotly_white",
        color_discrete_sequence=soft_palette
    )
    st.plotly_chart(fig3, use_container_width=True)
