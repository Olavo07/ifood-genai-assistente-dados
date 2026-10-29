"""
Assistente de Análise de Dados com IA — versão Dia 1 (sem IA ainda).

Por enquanto o app só faz: subir uma planilha (CSV ou Excel), mostrar uma
prévia dos dados e um gráfico simples escolhido pelo usuário. A parte de
perguntar em português e gerar SQL com um LLM entra no Dia 2.
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Assistente de Análise de Dados", page_icon="📊")

st.title("📊 Assistente de Análise de Dados com IA")
st.caption("Suba uma planilha para começar. (Por enquanto, sem IA — isso vem no próximo passo.)")

arquivo = st.file_uploader("Planilha (CSV ou Excel)", type=["csv", "xlsx"])

if arquivo is None:
    st.info("Nenhum arquivo enviado ainda. Use o dataset de exemplo em `data/pedidos.csv`.")
    st.stop()

if arquivo.name.endswith(".csv"):
    df = pd.read_csv(arquivo)
else:
    df = pd.read_excel(arquivo)

st.subheader("Prévia dos dados")
st.dataframe(df.head(20))

st.caption(f"{len(df)} linhas, {len(df.columns)} colunas.")

st.subheader("Gráfico rápido")

colunas_numericas = df.select_dtypes(include="number").columns.tolist()
colunas_categoricas = df.select_dtypes(exclude="number").columns.tolist()

if not colunas_numericas or not colunas_categoricas:
    st.warning("Não encontrei uma combinação de coluna categórica + numérica para montar o gráfico.")
else:
    indice_padrao = (
        colunas_categoricas.index("categoria_restaurante")
        if "categoria_restaurante" in colunas_categoricas
        else 0
    )
    col_categoria = st.selectbox("Agrupar por", colunas_categoricas, index=indice_padrao)
    col_valor = st.selectbox("Somar", colunas_numericas)

    resumo = df.groupby(col_categoria)[col_valor].sum().sort_values(ascending=False)
    st.bar_chart(resumo)
