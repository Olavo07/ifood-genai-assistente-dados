"""
Gera um dataset sintético de pedidos de delivery.

Os dados são inventados (não vêm de nenhuma empresa real) e servem só
para testar o app. O objetivo é ter uma base com colunas e padrões
realistas o suficiente para perguntas de análise fazerem sentido.
"""

import numpy as np
import pandas as pd

SEMENTE_ALEATORIA = 42
QUANTIDADE_PEDIDOS = 5000

CATEGORIAS_RESTAURANTE = [
    "Brasileira",
    "Italiana",
    "Japonesa",
    "Fast Food",
    "Pizzaria",
    "Doces e Sobremesas",
    "Saudável",
    "Árabe",
    "Churrasco",
    "Vegetariana",
]

BAIRROS = [
    "Pinheiros",
    "Moema",
    "Vila Mariana",
    "Tatuapé",
    "Santana",
    "Itaim Bibi",
    "Brooklin",
    "Vila Madalena",
    "Mooca",
    "Campo Belo",
]


def gerar_dataset(quantidade: int, semente: int) -> pd.DataFrame:
    rng = np.random.default_rng(semente)

    datas = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    data_pedido = rng.choice(datas, size=quantidade)

    categoria = rng.choice(CATEGORIAS_RESTAURANTE, size=quantidade)
    bairro = rng.choice(BAIRROS, size=quantidade)

    # Valor do pedido: a maioria fica entre R$ 25 e R$ 80, com uma cauda
    # de pedidos mais caros (distribuição log-normal).
    valor_pedido = np.round(rng.lognormal(mean=3.7, sigma=0.4, size=quantidade), 2)

    # Tempo de entrega em minutos: média ~38min, com variação.
    tempo_entrega_min = np.round(rng.normal(loc=38, scale=10, size=quantidade))
    tempo_entrega_min = np.clip(tempo_entrega_min, 10, 100).astype(int)

    # Avaliação (1 a 5): correlacionada com o tempo de entrega — pedidos
    # mais demorados tendem a ter nota um pouco pior. Isso cria um padrão
    # real para o LLM encontrar quando o usuário perguntar sobre isso.
    nota_base = 4.6 - (tempo_entrega_min - 38) / 40
    ruido = rng.normal(0, 0.6, size=quantidade)
    avaliacao = np.clip(np.round(nota_base + ruido), 1, 5).astype(int)

    return pd.DataFrame(
        {
            "data_pedido": data_pedido,
            "categoria_restaurante": categoria,
            "bairro": bairro,
            "valor_pedido": valor_pedido,
            "tempo_entrega_min": tempo_entrega_min,
            "avaliacao": avaliacao,
        }
    ).sort_values("data_pedido").reset_index(drop=True)


if __name__ == "__main__":
    df = gerar_dataset(QUANTIDADE_PEDIDOS, SEMENTE_ALEATORIA)
    caminho_saida = "data/pedidos.csv"
    df.to_csv(caminho_saida, index=False)
    print(f"Dataset gerado com {len(df)} linhas em '{caminho_saida}'.")
    print(df.head())
