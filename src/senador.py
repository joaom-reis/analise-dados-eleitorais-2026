
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json
from pathlib import Path
import os

from pathlib import Path

PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_GRAFICOS = PASTA_PROJETO / "graficos"
PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

URL_SENADOR = "https://resultados.tse.jus.br/oficial/ele2026/6259/dados/rj/rj-c0005-e006259-u.json"

HEADERS = {
    "User-Agent": "aula-ciencia-de-dados"
}

# Fazendo a requisição
resposta_senador = requests.get(
    URL_SENADOR,
    headers=HEADERS,
    timeout=30
)

# Verificar o status da requisição
print("Status da requisição:", resposta_senador.status_code)

# Interromper se houver erro HTTP
resposta_senador.raise_for_status()

# Converter a resposta para JSON
dados_senador = resposta_senador.json()

print("Tipo de dado:", type(dados_senador))
print("Chaves disponíveis:", list(dados_senador.keys()))

# Verificando as informações dos cargos
print("\nInformações dos cargos:")
print(dados_senador['carg'])

# Acessar a lista de agrupamentos partidários
agrupamentos = dados_senador['carg'][0]['agr']

# Mostrar os agrupamentos
print("\nAgrupamentos partidários:")
print(agrupamentos)

# Percorrer os agrupamentos partidários
for agrupamento in agrupamentos:
    print(agrupamento['nm'])

# Percorrer os partidos de cada agrupamento
for agrupamento in agrupamentos:
    for partido in agrupamento['par']:
        print(partido['sg'])

# Percorrer os candidatos de cada partido
for agrupamento in agrupamentos:
    for partido in agrupamento['par']:
        for candidato in partido['cand']:
            print(candidato['nmu'])

# Criar uma lista vazia para armazenar os candidatos
candidatos_senador = []

# Percorrer os agrupamentos partidários
for agrupamento in agrupamentos:

    # Percorrer os partidos
    for partido in agrupamento['par']:

        # Percorrer os candidatos
        for candidato in partido['cand']:

            # Adicionar os dados do candidato à lista
            candidatos_senador.append({
                'nome_completo': candidato['nm'],
                'nome_urna': candidato['nmu'],
                'partido': partido['sg'],
                'numero': candidato['n'],
                'votos': candidato['vap'],
                'percentual': candidato['pvap'],
                'situacao': candidato['st']
            })

# Exibir o primeiro candidato da lista
print("\nPrimeiro candidato:")
print(candidatos_senador[0])

# Transformar a lista em um DataFrame
df_senadores = pd.DataFrame(candidatos_senador)

# Tabela
print("\nTabela dos senadores:")
print(df_senadores)

# Convertendo votos para número inteiro
df_senadores['votos'] = df_senadores['votos'].astype(int)

# Convertendo percentual para número decimal
df_senadores['percentual'] = (
    df_senadores['percentual']
    .str.replace(',', '.', regex=False)
    .astype(float)
)

# Conferindo os tipos de dados
print("\nTipos de dados:")
print(df_senadores.dtypes)

# Contar candidatos por situação
situacao = df_senadores["situacao"].value_counts()

# Calcular percentual
percentual = situacao / situacao.sum() * 100

# Gráfico
plt.figure(figsize=(9, 5))

barras = plt.bar(
    situacao.index,
    situacao.values,
    color=["#2563EB", "#F59E0B"],
    width=0.55
)

for i, barra in enumerate(barras):
    quantidade = situacao.iloc[i]
    porcentagem = percentual.iloc[i]

    plt.text(
        barra.get_x() + barra.get_width() / 2,
        barra.get_height(),
        f"{quantidade} ({porcentagem:.1f}%)",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )

plt.title(
    "Situação dos candidatos ao Senado",
    fontsize=15,
    fontweight="bold"
)

plt.xlabel("Situação")
plt.ylabel("Quantidade de candidatos")

plt.ylim(0, situacao.max() * 1.2)

plt.grid(axis="y", linestyle="--", alpha=0.3)
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

plt.tight_layout()

# Salvar gráfico
plt.savefig(
    PASTA_GRAFICOS / "situacao_candidatos_senado.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Filtrar apenas os candidatos eleitos
eleitos = df_senadores[
    df_senadores["situacao"] == "Eleito"
].copy()

# Ordenar por quantidade de votos
eleitos = eleitos.sort_values(
    by="votos",
    ascending=False
)

# Gráfico
plt.figure(figsize=(9, 5))

barras = plt.bar(
    eleitos["nome_urna"],
    eleitos["votos"],
    color=["#16A34A", "#2563EB"],
    width=0.55
)

for barra in barras:
    votos = barra.get_height()

    plt.text(
        barra.get_x() + barra.get_width() / 2,
        votos,
        f"{votos:,.0f}".replace(",", "."),
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )

if len(eleitos) >= 2:
    diferenca = eleitos["votos"].iloc[0] - eleitos["votos"].iloc[1]

    plt.text(
        0.5,
        0.92,
        f"Diferença de votos: {diferenca:,.0f}".replace(",", "."),
        transform=plt.gca().transAxes,
        ha="center",
        fontsize=11,
        fontweight="bold",
        color="#16A34A"
    )

plt.title(
    "Comparativo de votos dos candidatos eleitos ao Senado",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel("Candidatos")
plt.ylabel("Quantidade de votos")

plt.grid(axis="y", linestyle="--", alpha=0.3)

plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

plt.tight_layout()

# Salvar gráfico
plt.savefig(
    PASTA_GRAFICOS / "comparativo_eleitos_senado.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Criar pasta dados
pasta_dados = Path(__file__).parent / "dados"

pasta_dados.mkdir(exist_ok=True)

df_csv_senadores = df_senadores.copy()

# Adicionar cargo
df_csv_senadores['cargo'] = 'Senador'

# Renomear coluna
df_csv_senadores = df_csv_senadores.rename(columns={
    'nome_completo': 'candidato'
})

# Organizar colunas
df_csv_senadores = df_csv_senadores[
    ['cargo', 'candidato', 'nome_urna', 'partido',
     'numero', 'votos', 'percentual', 'situacao']
]

# Definir caminho do arquivo
arquivo_csv = pasta_dados / 'senadores_2026.csv'

# Exportar CSV
df_csv_senadores.to_csv(
    arquivo_csv,
    index=False,
    encoding='utf-8-sig'
)

print("CSV dos senadores exportado com sucesso!")

# Abrir automaticamente o CSV
os.startfile(arquivo_csv)