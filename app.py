"""
Assistente de Análise de Dados com IA.

Fluxo: o usuário sobe uma planilha, faz uma pergunta em português, a IA
(Gemini) traduz a pergunta em uma consulta SQL, a consulta é validada por
segurança, executada no DuckDB, e a IA explica o resultado em português.
"""

import duckdb
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

import ia
import seguranca

load_dotenv()

st.set_page_config(page_title="Assistente de Análise de Dados", page_icon="📊")

st.title("📊 Assistente de Análise de Dados com IA")
st.caption("Suba uma planilha e faça uma pergunta em português sobre os dados.")


@st.cache_resource
def obter_cliente_ia():
    return ia.criar_cliente()

arquivo = st.file_uploader("Planilha (CSV ou Excel)", type=["csv", "xlsx"])

if arquivo is None:
    st.info("Nenhum arquivo enviado ainda. Use o dataset de exemplo em `data/pedidos.csv`.")
    st.stop()

if arquivo.name.endswith(".csv"):
    df = pd.read_csv(arquivo)
else:
    df = pd.read_excel(arquivo)

# Colunas de texto que "parecem" datas (ex: "2025-01-01") viram tipo data de
# verdade, para a IA poder gerar SQL com funções de data (strftime, EXTRACT etc).
for coluna in df.select_dtypes(include="object").columns:
    convertida = pd.to_datetime(df[coluna], errors="coerce", format="ISO8601")
    if convertida.notna().mean() > 0.9:
        df[coluna] = convertida

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

st.subheader("🤖 Pergunte aos dados")

with st.form("formulario_pergunta"):
    pergunta = st.text_input(
        "Sua pergunta em português",
        placeholder="Qual categoria de restaurante teve mais pedidos em março?",
    )
    enviar = st.form_submit_button("Perguntar")

if enviar and pergunta.strip():
    cliente, modelo = obter_cliente_ia()
    esquema = ia.montar_esquema(df)

    with st.spinner("Gerando a consulta SQL..."):
        try:
            sql_gerado = ia.gerar_sql(cliente, modelo, pergunta, esquema)
        except Exception as erro:
            st.error(f"Não consegui falar com a IA agora. Tente de novo em instantes. ({erro})")
            st.stop()

    if sql_gerado.upper().startswith("ERRO"):
        st.warning(sql_gerado)
        st.stop()

    erro_validacao = seguranca.validar_sql(sql_gerado)
    if erro_validacao:
        st.error(f"A consulta gerada não passou na validação de segurança: {erro_validacao}")
        with st.expander("Ver SQL gerado (bloqueado)"):
            st.code(sql_gerado, language="sql")
        st.stop()

    try:
        conexao = duckdb.connect()
        conexao.register("dados", df)
        resultado = conexao.execute(sql_gerado).df()
    except Exception as erro:
        st.error(
            "Não consegui executar essa consulta no banco — pode ser uma coluna "
            f"inexistente ou um erro de sintaxe. Tente reformular a pergunta. ({erro})"
        )
        with st.expander("Ver SQL gerado (com erro)"):
            st.code(sql_gerado, language="sql")
        st.stop()

    with st.spinner("Explicando o resultado..."):
        try:
            explicacao = ia.gerar_explicacao(cliente, modelo, pergunta, sql_gerado, resultado)
            st.success(explicacao)
        except Exception:
            st.info("Não consegui gerar a explicação em texto, mas aqui está o resultado:")

    st.dataframe(resultado)

    colunas_numericas_resultado = resultado.select_dtypes(include="number").columns.tolist()
    colunas_categoricas_resultado = resultado.select_dtypes(exclude="number").columns.tolist()
    if len(resultado) > 1 and colunas_numericas_resultado and colunas_categoricas_resultado:
        st.bar_chart(resultado.set_index(colunas_categoricas_resultado[0])[colunas_numericas_resultado[0]])

    with st.expander("Ver SQL gerado"):
        st.code(sql_gerado, language="sql")
