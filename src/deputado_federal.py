import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import matplotlib.pyplot as plt

import os
from pathlib import Path

import os

os.system("cls")

from pathlib import Path
import os

# Identificar a raiz do projeto
PASTA_PROJETO = Path(__file__).resolve().parent.parent

# Definir pastas de armazenamento
PASTA_GRAFICOS = PASTA_PROJETO / "graficos"
PASTA_DADOS = PASTA_PROJETO / "data" / "Processed"

# Criar pastas caso não existam
PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)
PASTA_DADOS.mkdir(parents=True, exist_ok=True)

URL_DEPUTADO_FEDERAL = "https://resultados.tse.jus.br/oficial/ele2026/6259/dados/rj/rj-c0006-e006259-u.json"

# Requisição à API
resposta = requests.get(
    URL_DEPUTADO_FEDERAL,
    headers={"User-Agent": "aula-ciencia-de-dados"},
    timeout=30
)

print("Status da requisição:", resposta.status_code)

resposta.raise_for_status()

# Transformando a resposta em JSON
dados = resposta.json()

print("\nTipo de dado:", type(dados))
print("\nChaves disponíveis:", list(dados.keys()))

partidos = dados["v"]

print("\nTipo de 'v':", type(partidos))
print("Quantidade de partidos/federações:", len(partidos))

# Explorando a estrutura dos partidos
partidos = dados["v"]

print("\nTipo de 'v':", type(partidos))
print("Quantidade de partidos/federações:", len(partidos))

# Verificando as chaves do dicionário
print("\nChaves disponíveis em 'v':")
print(list(partidos.keys()))

print("Status da requisição:", resposta.status_code)

# Explorando a estrutura dos cargos
print("\nESTRUTURA DA CHAVE CARG:")

cargos = dados["carg"]

print("Tipo de dado:", type(cargos))
print("Quantidade de cargos:", len(cargos))

# Primeiro cargo
primeiro_cargo = cargos[0]

print("\nChaves disponíveis no cargo:")
print(list(primeiro_cargo.keys()))

# Explorando os agrupamentos
agrupamentos = primeiro_cargo["agr"]

print("\nESTRUTURA DOS AGRUPAMENTOS:")
print("Tipo:", type(agrupamentos))
print("Quantidade:", len(agrupamentos))

print("\nPrimeiro agrupamento:")
print(agrupamentos[0])

print("\nChaves do primeiro agrupamento:")
print(list(agrupamentos[0].keys()))

# Explorando os partidos
partidos = agrupamentos[0]["par"]

print("\nESTRUTURA DOS PARTIDOS:")
print("Tipo:", type(partidos))
print("Quantidade de partidos:", len(partidos))

# Primeiro partido
primeiro_partido = partidos[0]

print("\nInformações do primeiro partido:")
print(primeiro_partido)

print("\nChaves do primeiro partido:")
print(list(primeiro_partido.keys()))

# Identificação do partido
print("\nSigla:", primeiro_partido["sg"])
print("Nome:", primeiro_partido["nm"])


# Lista para armazenar candidatos
lista_candidatos = []

# Percorrendo os cargos
for cargo in dados["carg"]:

    # Percorrendo os agrupamentos
    for agrupamento in cargo["agr"]:

        nome_agrupamento = agrupamento["nm"]
        tipo_agrupamento = agrupamento["tp"]

        # Percorrendo os partidos
        for partido in agrupamento["par"]:

            sigla_partido = partido["sg"]
            nome_partido = partido["nm"]

            # Percorrendo os candidatos
            for candidato in partido["cand"]:

                registro = {
                    "cargo": cargo["nmn"],
                    "agrupamento": nome_agrupamento,
                    "tipo_agrupamento": tipo_agrupamento,
                    "partido": nome_partido,
                    "sigla": sigla_partido,
                    "candidato": candidato["nm"],
                    "nome_urna": candidato["nmu"],
                    "numero": candidato["n"],
                    "nascimento": candidato["dt"],
                    "votos": candidato["vap"],
                    "percentual": candidato["pvap"],
                    "situacao": candidato["st"],
                    "situacao_votos": candidato["dvt"]
                }

                lista_candidatos.append(registro)

print("Total de candidatos:", len(lista_candidatos))


import pandas as pd

df = pd.DataFrame(lista_candidatos)

print("\nPrimeiros registros:")
print(df.head())

print("\nInformações do DataFrame:")
print(df.info())


# Converter para inteiros
df["votos"] = pd.to_numeric(df["votos"], errors="coerce")

# Converter decimal
df["percentual"] = (
    df["percentual"]
    .str.replace(",", ".", regex=False)
    .astype(float)
)

print("\nTipos de dados após conversão:")
print(df.dtypes)

print("\nConferência dos dados:")
print(df[["candidato", "votos", "percentual"]].head())


# Contagem por situação eleitoral
situacoes = df["situacao"].value_counts()

print("\nCandidatos por situação:")
print(situacoes)

# Total de candidatos eleitos
eleitos = df[df["situacao"].str.contains("Eleito", na=False)]

print("\nTotal de eleitos:", len(eleitos))

# Total de suplentes
suplentes = df[df["situacao"] == "Suplente"]

print("Total de suplentes:", len(suplentes))

# Total de não eleitos
nao_eleitos = df[df["situacao"] == "Não eleito"]

print("Total de não eleitos:", len(nao_eleitos))

# Filtrar somente os candidatos eleitos
eleitos = df[df["situacao"].str.startswith("Eleito", na=False)]

print("Total de eleitos:", len(eleitos))


situacoes = df["situacao"].value_counts()


# ==========================================
# GRÁFICO 1 - CANDIDATOS POR SITUAÇÃO ELEITORAL
# ==========================================

# Criar o gráfico
plt.figure(figsize=(10, 6))

barras = plt.bar(
    situacoes.index,
    situacoes.values
)

for barra in barras:
    altura = barra.get_height()

    plt.text(
        barra.get_x() + barra.get_width() / 2,
        altura,
        int(altura),
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )

plt.title(
    "Candidatos a Deputado Federal por Situação Eleitoral",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel("Situação eleitoral")
plt.ylabel("Quantidade de candidatos")

plt.xticks(rotation=15)
plt.grid(axis="y", linestyle="--", alpha=0.3)

plt.tight_layout()

plt.savefig(
    PASTA_GRAFICOS / "situacao_candidatos_deputados_federais.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ==========================================
# GRÁFICO 2 - DEPUTADOS ELEITOS POR TIPO
# ==========================================

# Filtrar os candidatos eleitos
eleitos = df[df["situacao"].str.startswith("Eleito", na=False)]

tipos_eleitos = eleitos["situacao"].value_counts()

plt.figure(figsize=(9, 6))

barras = plt.bar(
    tipos_eleitos.index,
    tipos_eleitos.values
)

for barra in barras:
    altura = barra.get_height()

    plt.text(
        barra.get_x() + barra.get_width() / 2,
        altura,
        int(altura),
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold"
    )

plt.title(
    "Deputados Federais Eleitos por Tipo de Eleição",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel("Tipo de eleição")
plt.ylabel("Quantidade de candidatos")

plt.ylim(0, max(tipos_eleitos.values) * 1.15)
plt.grid(axis="y", linestyle="--", alpha=0.3)

plt.tight_layout()

plt.savefig(
    PASTA_GRAFICOS / "deputados_federais_eleitos_por_tipo.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================
# GRÁFICO 3 - TOP 10 CANDIDATOS MAIS VOTADOS
# ==========================================


mais_votados = df.nlargest(10, "votos")
mais_votados = mais_votados.sort_values("votos", ascending=True)

plt.figure(figsize=(12, 7))

barras = plt.barh(
    mais_votados["nome_urna"],
    mais_votados["votos"]
)

for barra in barras:
    largura = barra.get_width()

    plt.text(
        largura,
        barra.get_y() + barra.get_height() / 2,
        f" {largura:,.0f}".replace(",", "."),
        va="center",
        fontsize=10,
        fontweight="bold"
    )

plt.title(
    "Top 10 Candidatos a Deputado Federal Mais Votados",
    fontsize=15,
    fontweight="bold"
)

plt.xlabel("Quantidade de votos")
plt.ylabel("Candidatos")

plt.grid(axis="x", linestyle="--", alpha=0.3)
plt.tight_layout()

plt.savefig(
    PASTA_GRAFICOS / "top_10_deputados_federais.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================
# EXPORTAÇÃO DO CSV
# ==========================================

# Criar cópia do DataFrame
df_csv_deputados = df.copy()

# Adicionar e organizar as informações
df_csv_deputados["cargo"] = "Deputado Federal"

df_csv_deputados = df_csv_deputados.rename(columns={
    "nome_completo": "candidato"
})

# Selecionar e organizar as colunas
df_csv_deputados = df_csv_deputados[
    [
        "cargo",
        "candidato",
        "nome_urna",
        "partido",
        "numero",
        "votos",
        "percentual",
        "situacao"
    ]
]

# Definir arquivo de destino
arquivo_csv = PASTA_DADOS / "deputados_federais_2026.csv"

# Exportar CSV
df_csv_deputados.to_csv(
    arquivo_csv,
    index=False,
    encoding="utf-8-sig"
)

# Abrir automaticamente no Excel
os.startfile(arquivo_csv)

print("CSV dos Deputados Federais exportado com sucesso!")
print(f"Arquivo salvo em: {arquivo_csv}")