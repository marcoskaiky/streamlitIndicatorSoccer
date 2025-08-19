import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import streamlit as st
import plotly.express as px

load_dotenv()

def conexao_banco():
  return psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
    
  )

@st.cache_data ###
def carregar_dados():
  conn = conexao_banco()
  df = pd.read_sql("""SELECT j.nome, t.nome AS time, e.gols, e.assistencias,
               (e.gols + e.assistencias) AS ga
        FROM jogadores j
        JOIN times t ON j.time_id = t.id
        JOIN estatisticas e ON j.id = e.jogador_id;""",conn)
  conn.close()
  return df

df = carregar_dados()

with st.sidebar:
  if st.button("Atualizar Dados"):
    st.cache_data.clear()

  st.markdown("---")
  st.metric("Total de gols",int(df["gols"].sum()))
  st.metric("Total de assistencias",int(df["assistencias"].sum()))
  st.metric("Total de jogadores inscritos",int(df["nome"].nunique())) #####

top_gols = df.nlargest(10, "gols")
st.title("Top 10 Artilheiros")
st.plotly_chart(
  px.bar(
    top_gols,
    x="nome",
    y="gols",
    color="time"
  )
)
st.markdown("---")  


top_ga = df.nlargest(10, "ga")
st.title("TOP 10 saldo G+A")
fig = px.scatter_3d(
  top_ga,
  x="nome",
  y="time",
  z="ga",
  color="time",
  size="ga",
  hover_name="nome"
)
st.plotly_chart(fig)
st.markdown("---")


gols_por_time = df.groupby("time")["gols"].sum().reset_index() ###
st.title("Gols por time")
st.plotly_chart(
  px.pie(
    gols_por_time,
    names="time",
    values="gols",
    
  )
)
