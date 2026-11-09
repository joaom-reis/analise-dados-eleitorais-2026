import requests
import pandas as pd
import matplotlib.pyplot as plt
import json
import os


os.system("cls")

import os
from pathlib import Path
import matplotlib.pyplot as plt

# Identificar a pasta principal do projeto
pasta_projeto = Path(__file__).resolve().parent.parent

# Criar pasta de gráficos
pasta_graficos = pasta_projeto / "graficos"
pasta_graficos.mkdir(parents=True, exist_ok=True)

# Criar pasta de dados processados
pasta_dados = pasta_projeto / "data" / "processed"
pasta_dados.mkdir(parents=True, exist_ok=True)

url = "https://resultados.tse.jus.br/oficial/ele2026/6259/dados/rj/rj-c0007-e006259-u.json"

resposta = requests.get(url)

print("Status da requisição:", resposta.status_code)

# Converter a resposta para JSON
dados = resposta.json()

print("Tipo de dado:", type(dados))

print("\nChaves disponíveis:", list(dados.keys()))

# Verificar informações do cargo
print("Informações dos cargos:")
print(dados["carg"])


print("\nEstrutura de carg:")
print(json.dumps(dados["carg"], indent=4, ensure_ascii=False)[:10000])

# dados de votação
print(json.dumps(dados['v'], indent=4, ensure_ascii=False)[:5000])

print("\nTipo de dados de 'cand':", type(dados.get('cand')))

print("\nChaves disponíveis em 'dados':")
print(dados.keys())

# Extrair candidatos a Deputado Estadual

candidatos = []

for cargo in dados["carg"]:

    for agrupamento in cargo["agr"]:

        for partido in agrupamento["par"]:

            for candidato in partido["cand"]:

                registro = {
                    "cargo": cargo["nmn"],
                    "agrupamento": agrupamento["nm"],
                    "tipo_agrupamento": agrupamento["tp"],
                    "partido": partido["nm"],
                    "sigla": partido["sg"],
                    "candidato": candidato["nm"],
                    "nome_urna": candidato["nmu"],
                    "numero": candidato["n"],
                    "votos": candidato["vap"],
                    "percentual": candidato["pvap"],
                    "situacao": candidato["st"],
                    "validade_votos": candidato["dvt"]
                }

                candidatos.append(registro)

# Exibir quantidade de candidatos
print("\nTotal de candidatos:", len(candidatos))

df = pd.DataFrame(candidatos)

print("\nPrimeiros candidatos:")
print(df.head(10).to_string(index=False))

df["votos"] = pd.to_numeric(df["votos"], errors="coerce")

# Converter percentual para número decimal
df["percentual"] = (
    df["percentual"]
    .str.replace(",", ".", regex=False)
    .astype(float)
)

print("\nTipos de dados:")
print(df.dtypes)

# Verificar candidatos por situação
print("\nQuantidade de candidatos por situação:")
print(df["situacao"].value_counts())

print("\nTotal de candidatos:", len(df))

# Quantidade de candidatos por partido
candidatos_partido = (
    df.groupby("sigla")["candidato"]
    .count()
    .sort_values(ascending=False)
)

print("\nQuantidade de candidatos por partido:")
print(candidatos_partido)

# Total de votos por partido
votos_partido = (
    df.groupby("sigla")["votos"]
    .sum()
    .sort_values(ascending=False)
)

print("\nTotal de votos por partido:")
print(votos_partido)

# ==========================================
# GRÁFICO 1 - CANDIDATOS POR SITUAÇÃO ELEITORAL
# ==========================================

situacao = df["situacao"].value_counts()

plt.figure(figsize=(10, 6))

barras = plt.bar(
    situacao.index,
    situacao.values
)

plt.title(
    "Deputado Estadual - Candidatos por Situação Eleitoral",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel("Situação eleitoral")
plt.ylabel("Quantidade de candidatos")

plt.bar_label(barras, padding=3, fontsize=10)

plt.xticks(rotation=15)
plt.tight_layout()

# Salvar gráfico
plt.savefig(
    pasta_graficos / "deputados_estaduais_situacao.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ==========================================
# GRÁFICO 2 - DEPUTADOS ESTADUAIS ELEITOS POR PARTIDO
# ==========================================

eleitos = df[
    df["situacao"].isin(["Eleito por QP", "Eleito por média"])
]

eleitos_partido = (
    eleitos.groupby("sigla")
    .size()
    .sort_values(ascending=False)
)

plt.figure(figsize=(12, 7))

barras = plt.bar(
    eleitos_partido.index,
    eleitos_partido.values
)

plt.title(
    "Deputado Estadual - Eleitos por Partido",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel("Partido")
plt.ylabel("Quantidade de eleitos")

plt.bar_label(barras, padding=3, fontsize=10)

plt.xticks(rotation=45, ha="right")
plt.tight_layout()

# Salvar gráfico
plt.savefig(
    pasta_graficos / "deputados_estaduais_por_partido.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ==========================================
# EXPORTAÇÃO CSV - DEPUTADOS ESTADUAIS
# ==========================================

# Criar uma cópia dos dados
df_csv_deputados = df.copy()

# Adicionar coluna cargo
df_csv_deputados["cargo"] = "Deputado Estadual"

# Renomear coluna
df_csv_deputados = df_csv_deputados.rename(
    columns={"nome_completo": "candidato"}
)

# Organizar as 8 colunas padronizadas
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

# Definir caminho do arquivo CSV
arquivo_csv = pasta_dados / "deputados_estaduais_2026.csv"

# Exportar CSV
df_csv_deputados.to_csv(
    arquivo_csv,
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# CONFIRMAÇÃO DA EXPORTAÇÃO
# ==========================================

print("\n==========================================")
print("DEPUTADO ESTADUAL - EXPORTAÇÃO CONCLUÍDA")
print("==========================================")

print("\nCSV exportado com sucesso!")
print(f"Local: {arquivo_csv}")

print("\nPrimeiros registros:")
print(df_csv_deputados.head())

print("\nGráficos salvos:")
print("1. deputados_estaduais_situacao.png")
print("2. deputados_estaduais_por_partido.png")

print("\n==========================================")


# Abrir arquivo CSV automaticamente (Windows)
os.startfile(arquivo_csv)
