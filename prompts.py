"""
Prompts usados para falar com o modelo de IA (Gemini).

Mantemos os prompts aqui, separados da lógica do app, para que fiquem
fáceis de ler, ajustar e explicar (decisões de prompt engineering).
"""

PROMPT_SQL = """Você traduz perguntas em português para consultas SQL no dialeto do DuckDB.

Existe uma única tabela chamada "dados" com este esquema:
{esquema}

Regras obrigatórias:
- Responda APENAS com a consulta SQL. Sem explicação, sem markdown, sem ponto e vírgula no final.
- Use apenas comandos de leitura: SELECT ou WITH.
- Use somente a tabela "dados" e as colunas listadas no esquema acima — não invente colunas.
- Se a pergunta não puder ser respondida com os dados disponíveis (coluna inexistente, pergunta ambígua, pede algo fora do escopo dos dados), responda exatamente: ERRO: <motivo breve em português>

Pergunta: {pergunta}
"""

PROMPT_EXPLICACAO = """Pergunta original do usuário: {pergunta}

Consulta SQL executada: {sql}

Resultado da consulta (primeiras linhas):
{resultado}

Escreva de 1 a 2 frases curtas em português respondendo diretamente a pergunta,
usando os números do resultado. Não repita a consulta SQL. Não use markdown.
Se o resultado estiver vazio, diga isso claramente.
"""


def montar_prompt_sql(esquema: str, pergunta: str) -> str:
    return PROMPT_SQL.format(esquema=esquema, pergunta=pergunta)


def montar_prompt_explicacao(pergunta: str, sql: str, resultado_texto: str) -> str:
    return PROMPT_EXPLICACAO.format(pergunta=pergunta, sql=sql, resultado=resultado_texto)
