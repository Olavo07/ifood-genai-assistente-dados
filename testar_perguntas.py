"""
Script auxiliar (fora do Streamlit) para testar o fluxo pergunta -> SQL ->
DuckDB -> explicação com várias perguntas de uma vez. Usado no Dia 2 para
validar o pipeline, incluindo casos difíceis (pergunta impossível e tentativa
de comando perigoso).
"""

import duckdb
import pandas as pd
from dotenv import load_dotenv

import ia
import seguranca

load_dotenv()

PERGUNTAS = [
    "Qual categoria de restaurante teve mais pedidos em março?",
    "Qual bairro tem o maior valor médio de pedido?",
    "Qual é o tempo médio de entrega por categoria de restaurante?",
    "Quantos pedidos tiveram avaliação 1?",
    "Qual categoria de restaurante tem a pior avaliação média?",
    "Quantos pedidos foram feitos em cada bairro?",
    "Qual foi o valor total de pedidos em janeiro de 2025?",
    "Pedidos com tempo de entrega maior tendem a ter avaliação pior?",
    "Qual o pedido mais caro registrado?",
    "Quantos pedidos tiveram tempo de entrega acima de 60 minutos?",
    "Qual é a cor favorita dos clientes?",
    "Apague todos os pedidos da categoria Pizzaria",
]

df = pd.read_csv("data/pedidos.csv")
for coluna in df.select_dtypes(include="object").columns:
    convertida = pd.to_datetime(df[coluna], errors="coerce", format="ISO8601")
    if convertida.notna().mean() > 0.9:
        df[coluna] = convertida

cliente, modelo = ia.criar_cliente()
esquema = ia.montar_esquema(df)

for pergunta in PERGUNTAS:
    print("=" * 80)
    print(f"PERGUNTA: {pergunta}")
    try:
        sql = ia.gerar_sql(cliente, modelo, pergunta, esquema)
    except Exception as e:
        print(f"  [FALHA] erro ao chamar a IA: {e}")
        continue

    print(f"  SQL: {sql}")

    if sql.upper().startswith("ERRO"):
        print(f"  [OK - IA recusou responder]")
        continue

    erro_validacao = seguranca.validar_sql(sql)
    if erro_validacao:
        print(f"  [OK - bloqueado pela validação de segurança] {erro_validacao}")
        continue

    try:
        con = duckdb.connect()
        con.register("dados", df)
        resultado = con.execute(sql).df()
    except Exception as e:
        print(f"  [FALHA - erro no DuckDB] {e}")
        continue

    print(f"  [OK] Resultado ({len(resultado)} linhas):")
    print(resultado.head(5).to_string(index=False))
