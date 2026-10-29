"""
Validação da consulta SQL gerada pela IA antes de executar no banco.

Regra central do projeto: NUNCA executar código Python gerado pela IA, e só
executar SQL que comece com SELECT/WITH e não contenha comandos que alterem
dados, acessem arquivos ou mudem a configuração do banco.
"""

import re

COMANDOS_PROIBIDOS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE",
    "ATTACH", "DETACH", "COPY", "PRAGMA", "INSTALL", "LOAD", "EXPORT",
    "IMPORT", "CALL", "SET", "GRANT", "REVOKE",
]


def validar_sql(sql: str) -> str | None:
    """Retorna uma mensagem de erro se a consulta não for segura, ou None se estiver OK."""
    sql_limpo = sql.strip().rstrip(";").strip()

    if not sql_limpo:
        return "A IA não retornou nenhuma consulta."

    primeira_palavra = sql_limpo.split(None, 1)[0].upper()
    if primeira_palavra not in ("SELECT", "WITH"):
        return f"A consulta precisa começar com SELECT ou WITH (veio '{primeira_palavra}')."

    if ";" in sql_limpo:
        return "A consulta contém mais de um comando (ponto e vírgula no meio)."

    sql_maiusculo = sql_limpo.upper()
    for comando in COMANDOS_PROIBIDOS:
        if re.search(rf"\b{comando}\b", sql_maiusculo):
            return f"A consulta contém um comando não permitido: {comando}."

    return None
