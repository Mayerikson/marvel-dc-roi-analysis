# Streamlit app: Análise ROI Marvel vs DC (interface em Português)
# Salve como app.py e faça deploy no Streamlit Cloud.

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px

# --- Configuração da página ---
st.set_page_config(layout="wide", page_title="Marvel vs DC – Análise de ROI")

st.title("Análise de ROI: Marvel vs DC")
st.markdown("""
Aplicação para comparar ROI, volatilidade e relacionar avaliações com performance financeira.
Interface totalmente em português.
""")

# --- Função para ler CSV com tratamento de erros ---
@st.cache_data
def read_csv_flexible(path):
    for enc in ['utf-8', 'latin', 'cp1252']:
        for sep in [',', ';', '\t', '|']:
            try:
                df = pd.read_csv(path, encoding=enc, sep=sep)
                return df
            except Exception:
                continue
    return None

# --- Leitura dos arquivos ---
df_fin = read_csv_flexible("financeiro.csv")
df_dc = read_csv_flexible("personagensdc.csv")
df_marvel = read_csv_flexible("personagensmarvel.csv")
df_ratings = read_csv_flexible("ratings.csv")

# --- Verificação inicial ---
if df_fin is None or df_dc is None or df_marvel is None or df_ratings is None:
    st.error("Erro ao ler um ou mais arquivos CSV. Verifique se eles estão na pasta do projeto e com formato válido.")
    st.stop()

# --- Cálculo de ROI ---
if 'receita' in df_fin.columns and 'orcamento' in df_fin.columns:
    df_fin['roi'] = (df_fin['receita'] - df_fin['orcamento']) / df_fin['orcamento']
else:
    st.error("O arquivo financeiro.csv precisa ter as colunas 'receita' e 'orcamento'.")
    st.stop()

# --- Cálculo por estúdio ---
results = []
if 'studio' in df_fin.columns:
    for studio in df_fin['studio'].unique():
        df_studio = df_fin[df_fin['studio'] == studio].copy()

        if 'release_date' in df_studio.columns:
            df_studio['release_date'] = pd.to_datetime(df_studio['release_date'], errors='coerce')
            df_studio = df_studio.sort_values('release_date', ascending=False)

        top15 = df_studio.head(15)

        if 'roi' in df_studio.columns and not top15['roi'].isna().all():
            results.append({
                'studio': studio,
                'median_roi_15_recent': top15['roi'].median(),
                'n_filmes': len(top15)
            })
else:
    st.error("O arquivo financeiro.csv precisa ter a coluna 'studio'.")
    st.stop()

# --- Resultado da tabela ---
if not results:
    st.error("Nenhum resultado encontrado. Verifique se as colunas 'studio', 'release_date' e 'roi' estão corretas.")
else:
    res_df = pd.DataFrame(results)
    if 'median_roi_15_recent' in res_df.columns:
        res_df = res_df.sort_values('median_roi_15_recent', ascending=False)
        st.subheader("Mediana de ROI (15 filmes mais recentes por estúdio)")
        st.dataframe(res_df)
    else:
        st.error("A coluna 'median_roi_15_recent' não foi criada.")

# --- Boxplot ROI por estúdio ---
if 'studio' in df_fin.columns and 'roi' in df_fin.columns:
    st.subheader("Distribuição de ROI por Estúdio")
    fig_box = px.box(df_fin, x="studio", y="roi", points="all", title="Boxplot ROI por Estúdio")
    st.plotly_chart(fig_box, use_container_width=True)

# --- Scatter IMDB vs ROI ---
if 'imdb' in df_ratings.columns and 'roi' in df_fin.columns:
    df_merge = pd.merge(df_fin, df_ratings, on="id", how="left")
    st.subheader("Relação IMDB vs ROI")
    fig_scatter = px.scatter(df_merge, x="imdb", y="roi", color="studio",
                             title="IMDB Score vs ROI", trendline="ols")
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("Não foi possível criar scatter IMDB vs ROI. Colunas 'imdb' e/ou 'id' ausentes.")

# --- Top 15 filmes por ROI ---
if 'roi' in df_fin.columns:
    st.subheader("Top 15 Filmes por ROI")
    top15_filmes = df_fin.sort_values('roi', ascending=False).head(15)
    st.dataframe(top15_filmes)
else:
    st.warning("Coluna 'roi' não encontrada para gerar Top 15.")
