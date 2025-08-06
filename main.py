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
    df = pd.read_sql("""
        SELECT j.nome, t.nome AS time, e.gols, e.assistencias,
               (e.gols + e.assistencias) AS ga
        FROM jogadores j
        JOIN times t ON j.time_id = t.id
        JOIN estatisticas e ON j.id = e.jogador_id;
    """, conn)
    conn.close()
    return df

with st.sidebar:
    if st.button("Recarregar Dados"):
        st.cache_data.clear()
    df_full = carregar_dados()
    times = ["Todos"] + df_full["time"].unique().tolist()
    st.markdown("---")
    filtro_time = st.selectbox("Time", times)

df = df_full if filtro_time == "Todos" else df_full[df_full["time"] == filtro_time]

k1, k2, k3 = st.columns(3)
k1.metric("⚽Gols", int(df["gols"].sum()))
k2.metric("🎯Assistências", int(df["assistencias"].sum()))
k3.metric("🙋Jogadores", int(df["nome"].nunique()))
st.markdown("---")

top_gols = df.nlargest(10, "gols")
st.title("Top 10 Jogadores com Mais Gols")
st.plotly_chart(px.bar(top_gols, x="nome", y="gols", color="time"), use_container_width=True)
st.markdown("---")

top_ga = df.nlargest(10, "ga")
st.title("Top 10 Jogadores com Mais Gols e Assistências")
st.plotly_chart(px.bar(top_ga, x="nome", y="ga", color="time"), use_container_width=True)
st.markdown("---")

gols_por_time = df.groupby("time")["gols"].sum().reset_index()
st.title("Gols por Time")
st.plotly_chart(px.pie(gols_por_time, names="time", values="gols"), use_container_width=True)
st.markdown("---")
