# Streamlit app: Análise ROI Marvel vs DC (interface em Português)
# Salve como streamlit_app.py e faça deploy no Streamlit Cloud.

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Marvel vs DC — Análise de ROI")

st.title("Análise de ROI: Marvel vs DC")
st.markdown("Aplicação para comparar ROI, volatilidade e relacionar avaliações com performance financeira. Interface totalmente em português.")

@st.cache_data
def read_csv_flexible(path):
    for enc in ['utf-8','latin1','cp1252']:
        for sep in [',',';','\t','|']:
            try:
                return pd.read_csv(path, encoding=enc, sep=sep, engine='python')
            except Exception:
                pass
    return None

# Uploads
st.sidebar.header('Carregar arquivos (ou deixe os arquivos no repositório)')
fin_file = st.sidebar.file_uploader('financeiro.csv', type=['csv'])
ratings_file = st.sidebar.file_uploader('ratings.csv', type=['csv'])
pm_file = st.sidebar.file_uploader('personagensmarvel.csv', type=['csv'])
pd_file = st.sidebar.file_uploader('personagensdc.csv', type=['csv'])

# Tentar ler a partir de arquivos locais se não houver upload (útil no deploy a partir do repo)
base_paths = {
    'financeiro': Path('financeiro.csv'),
    'ratings': Path('ratings.csv'),
    'pm': Path('personagensmarvel.csv'),
    'pd': Path('personagensdc.csv')
}

if fin_file is not None:
    df_fin = pd.read_csv(fin_file, engine='python')
elif base_paths['financeiro'].exists():
    df_fin = read_csv_flexible(base_paths['financeiro'])
else:
    st.error('Por favor carregue financeiro.csv para rodar a aplicação.')
    st.stop()

# Try to read other files (optional)
if ratings_file is not None:
    df_ratings = pd.read_csv(ratings_file, engine='python')
elif base_paths['ratings'].exists():
    df_ratings = read_csv_flexible(base_paths['ratings'])
else:
    df_ratings = pd.DataFrame()

if pm_file is not None:
    df_pm = pd.read_csv(pm_file, engine='python')
elif base_paths['pm'].exists():
    df_pm = read_csv_flexible(base_paths['pm'])
else:
    df_pm = pd.DataFrame()

if pd_file is not None:
    df_pd = pd.read_csv(pd_file, engine='python')
elif base_paths['pd'].exists():
    df_pd = read_csv_flexible(base_paths['pd'])
else:
    df_pd = pd.DataFrame()

# Normalização de nomes de coluna
cols_map = {
    'Original Title':'Original_Title',
    'Original_Title':'Original_Title',
    'Company':'company',
    'Release':'release',
    'Gross Worldwide':'Gross_Worldwide',
    'Gross\xa0Worldwide':'Gross_Worldwide',
    'Budget':'Budget'
}
for k,v in cols_map.items():
    if k in df_fin.columns and v not in df_fin.columns:
        df_fin = df_fin.rename(columns={k:v})

# Limpeza de valores numéricos
for col in ['Budget','Gross_Worldwide']:
    if col in df_fin.columns:
        df_fin[col] = pd.to_numeric(df_fin[col].astype(str).str.replace(',','').str.replace(' ','').str.replace('\xa0',''), errors='coerce')

# Criar ROI com segurança
if 'Budget' in df_fin.columns and 'Gross_Worldwide' in df_fin.columns:
    df_fin['ROI'] = np.where(df_fin['Budget']>0, df_fin['Gross_Worldwide']/df_fin['Budget'], np.nan)
else:
    st.error('As colunas Budget e Gross Worldwide são necessárias no arquivo financeiro.')
    st.stop()

# Parse release
if 'release' in df_fin.columns:
    df_fin['release_dt'] = pd.to_datetime(df_fin['release'], errors='coerce')
else:
    df_fin['release_dt'] = pd.NaT

# Filtros
companies = df_fin['company'].dropna().unique().tolist()
selected = st.sidebar.multiselect('Estúdios', companies, default=companies)

dff = df_fin[df_fin['company'].isin(selected)].copy()

st.header('Métrica 1 — Mediana do ROI dos 15 filmes mais recentes por estúdio')
results = []
for comp in selected:
    sub = dff[dff['company']==comp].sort_values('release_dt', ascending=False)
    top15 = sub.head(15)
    med = top15['ROI'].median()
    results.append({'company':comp,'median_roi_15_recent':med,'n_in_sample':len(top15)})
res_df = pd.DataFrame(results).sort_values('median_roi_15_recent', ascending=False)
st.dataframe(res_df)

st.header('Gráficos e análises')
col1, col2 = st.columns(2)
with col1:
    st.subheader('Boxplot de ROI por estúdio')
    fig = px.box(dff, x='company', y='ROI', points='all', title='Distribuição de ROI por estúdio')
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.subheader('Volatilidade (min / max / amplitude)')
    vol = []
    for comp in selected:
        sub = dff[dff['company']==comp]['ROI'].dropna()
        if len(sub)>0:
            vol.append({'company':comp,'min':sub.min(),'max':sub.max(),'amplitude':sub.max()-sub.min(),'std':sub.std(ddof=0)})
    st.table(pd.DataFrame(vol))

# Scatter IMDB x ROI (se ratings disponíveis)
if not df_ratings.empty:
    st.subheader('Scatter: IMDB Score vs ROI')
    # tentar encontrar coluna de título e coluna imdb
    title_cols = [c for c in df_ratings.columns if 'movie' in c.lower() or 'title' in c.lower() or 'original' in c.lower()]
    imdb_cols = [c for c in df_ratings.columns if 'imdb' in c.lower()]
    if title_cols and imdb_cols:
        tcol = title_cols[0]
        icol = imdb_cols[0]
        df_ratings['title_key'] = df_ratings[tcol].astype(str).str.lower().str.strip()
        dff['title_key'] = dff['Original_Title'].astype(str).str.lower().str.strip()
        merged = dff.merge(df_ratings[['title_key',icol]], on='title_key', how='left')
        merged[icol] = pd.to_numeric(merged[icol], errors='coerce')
        merged = merged.dropna(subset=[icol,'ROI'])
        if not merged.empty:
            fig2 = px.scatter(merged, x=icol, y='ROI', color='company', trendline='ols', title='IMDB Score vs ROI')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info('Não há pares válidos IMDB x ROI após o join dos títulos.')
    else:
        st.info('Arquivo ratings carregado mas colunas de título/IMDB não foram detectadas automaticamente.')

st.header('Top 15 filmes mais recentes por estúdio (detalhe)')
tabs = st.tabs(selected)
for i,comp in enumerate(selected):
    with tabs[i]:
        sub = dff[dff['company']==comp].sort_values('release_dt', ascending=False).head(15)
        st.dataframe(sub[['Original_Title','release','Budget','Gross_Worldwide','ROI']].reset_index(drop=True))

st.header('Guia de Deploy — Streamlit Cloud (rápido)')
st.markdown(
"""
1. Crie um repositório no GitHub com este arquivo `streamlit_app.py` e os CSVs `financeiro.csv`, `ratings.csv`, `personagensmarvel.csv`, `personagensdc.csv` (ou deixe o app pedir upload).  
2. No https://streamlit.io/cloud, conecte seu GitHub e selecione o repositório.  
3. Configure a branch e o comando de execução (padrão `streamlit run streamlit_app.py`).  
4. Suba e aguarde o build — a app ficará pública no domínio streamlit.app.  

Dica: se preferir não subir os CSVs no repo, use o upload via sidebar (útil para dados sensíveis).
"""
)

st.sidebar.markdown('Feito por: Análise ROI — adapte conforme necessário')

# Fim do app
