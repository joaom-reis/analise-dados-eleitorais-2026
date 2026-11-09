import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests



import requests
import json

from pathlib import Path

# Identificar a pasta principal do projeto
PASTA_PROJETO = Path(__file__).resolve().parent.parent

# Criar caminho da pasta de gráficos
PASTA_GRAFICOS = PASTA_PROJETO / "graficos"

# Criar a pasta caso ela não exista
PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

URL = "https://resultados.tse.jus.br/oficial/ele2026/6257/dados/br/br-c0001-e006257-u.json"


HEADERS = {
    "User-Agent": "aula-ciencia-de-dados"
}

# Fazendo a requisição ao servidor
resposta = requests.get(URL, headers=HEADERS, timeout=30)
print("Status da requisição:", resposta.status_code)


resposta.raise_for_status()
dados = resposta.json()


print("\nTipo de dado:", type(dados))
print("\nChaves disponíveis:", list(dados.keys()))



print("Código do cargo:", dados.get("carg"))
print("Tipo de abrangência:", dados.get("tpabr"))
print("Código da abrangência:", dados.get("cdabr"))

# Investigando registros eleitorais
registros = dados.get("v")

print("\nTipo da variável 'v':", type(registros))

if isinstance(registros, list):
    print("Quantidade de registros:", len(registros))

    if registros:
        print("\nPrimeiro registro:")
        print(json.dumps(registros[0], indent=2, ensure_ascii=False))

elif isinstance(registros, dict):
    print("Chaves dos registros:", list(registros.keys()))

else:
    print("Conteúdo:", registros)

# Lista que armazenará os dados dos candidatos
lista_candidatos = []


for cargo in dados["carg"]:

    
    for agrupamento in cargo.get("agr", []):

        for partido in agrupamento.get("par", []):

            for candidato in partido.get("cand", []):

                registro = {
                    "cargo": cargo.get("nmn"),
                    "candidato": candidato.get("nm"),
                    "nome_urna": candidato.get("nmu"),
                    "partido": partido.get("sg"),
                    "numero": candidato.get("n"),
                    "votos": candidato.get("vap"),
                    "percentual": candidato.get("pvap"),
                    "situacao": candidato.get("st")
                }

                lista_candidatos.append(registro)

# Transformando a lista em DataFrame
df_presidente = pd.DataFrame(lista_candidatos)

# Exibindo a tabela
print(df_presidente)

# Convertendo para números inteiros
df_presidente["votos"] = pd.to_numeric(
    df_presidente["votos"]
)

# Substituindo vírgula por ponto nos percentuais
df_presidente["percentual"] = (
    df_presidente["percentual"].str.replace(",", ".", regex=False)
)

# Convertendo percentual para número decimal
df_presidente["percentual"] = pd.to_numeric(
    df_presidente["percentual"]
)

# Conferindo os tipos de dados
print(df_presidente.dtypes)

# Conferindo valores ausentes
print("\nValores ausentes:")
print(df_presidente.isnull().sum())

# Conferindo candidatos duplicados
print("\nCandidatos duplicados:")
print(df_presidente["candidato"].duplicated().sum())

# Estatísticas descritivas
print("\nEstatísticas dos votos:")
print(df_presidente["votos"].describe())

# Ordenar candidatos pela quantidade de votos
df_grafico = df_presidente.sort_values(
    by="votos",
    ascending=False
)

# Gráfico
plt.figure(figsize=(12, 6))

sns.barplot(
    data=df_grafico,
    x="votos",
    y="nome_urna"
)

plt.title("Votação dos candidatos à Presidência")
plt.xlabel("Quantidade de votos")
plt.ylabel("Candidatos")

plt.tight_layout()

# Salvar gráfico
plt.savefig(
    PASTA_GRAFICOS / "votacao_presidente.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Medidas estatísticas dos votos
mediana = df_presidente["votos"].median()

desvio_padrao = df_presidente["votos"].std()

q1 = df_presidente["votos"].quantile(0.25)
q3 = df_presidente["votos"].quantile(0.75)

iqr = q3 - q1

print("Mediana:", mediana)
print("Desvio padrão:", desvio_padrao)
print("Primeiro quartil:", q1)
print("Terceiro quartil:", q3)
print("Amplitude interquartil:", iqr)

df_presidente.to_csv(
    "presidente_2026.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Arquivo CSV salvo com sucesso!")