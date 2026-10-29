"""
Integração com o Gemini: montar o esquema da tabela para o prompt,
pedir a consulta SQL e pedir a explicação do resultado em português.
"""

import os
import re

import pandas as pd
from google import genai
from google.genai import types

import prompts

MODELO_PADRAO = "gemini-3.5-flash-lite"
MAX_VALORES_UNICOS_NO_ESQUEMA = 20


def criar_cliente() -> tuple[genai.Client, str]:
    """Lê a chave e o modelo do ambiente (.env) e cria o cliente do Gemini."""
    chave = os.environ["GEMINI_API_KEY"]
    modelo = os.environ.get("GEMINI_MODEL", MODELO_PADRAO)
    cliente = genai.Client(api_key=chave, http_options=types.HttpOptions(timeout=15_000))
    return cliente, modelo


def montar_esquema(df: pd.DataFrame) -> str:
    """Descreve as colunas do DataFrame (nome, tipo e valores possíveis) para o prompt."""
    linhas = []
    for coluna in df.columns:
        if pd.api.types.is_numeric_dtype(df[coluna]):
            tipo = "número"
        elif pd.api.types.is_datetime64_any_dtype(df[coluna]):
            tipo = "data"
        else:
            tipo = "texto"

        descricao = f"- {coluna} ({tipo})"
        if tipo == "texto":
            valores_unicos = df[coluna].dropna().unique()
            if len(valores_unicos) <= MAX_VALORES_UNICOS_NO_ESQUEMA:
                descricao += f" — valores possíveis: {', '.join(map(str, valores_unicos))}"
        linhas.append(descricao)

    exemplo = df.head(3).to_string(index=False)
    return "\n".join(linhas) + f"\n\nExemplo de linhas:\n{exemplo}"


def extrair_sql(texto: str) -> str:
    """Remove blocos de markdown (```sql ... ```) caso o modelo os inclua na resposta."""
    texto = texto.strip()
    correspondencia = re.search(r"```(?:sql)?\s*(.*?)```", texto, re.DOTALL | re.IGNORECASE)
    if correspondencia:
        return correspondencia.group(1).strip()
    return texto


def gerar_sql(cliente: genai.Client, modelo: str, pergunta: str, esquema: str) -> str:
    prompt = prompts.montar_prompt_sql(esquema, pergunta)
    resposta = cliente.models.generate_content(model=modelo, contents=prompt)
    return extrair_sql(resposta.text)


def gerar_explicacao(cliente: genai.Client, modelo: str, pergunta: str, sql: str, resultado: pd.DataFrame) -> str:
    resultado_texto = resultado.head(10).to_string(index=False) if not resultado.empty else "(nenhuma linha retornada)"
    prompt = prompts.montar_prompt_explicacao(pergunta, sql, resultado_texto)
    resposta = cliente.models.generate_content(model=modelo, contents=prompt)
    return resposta.text.strip()
