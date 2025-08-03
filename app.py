import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Marvel vs DC: Análise de ROI",
    page_icon="🦸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado minimalista
st.markdown("""
<style>
    :root {
        --marvel-red: #ED1D24;
        --dc-blue: #0078F0;
        --neutral: #2E2E2E;
    }
    
    .stApp {
        font-family: 'Arial', sans-serif;
    }
    
    .header-marvel {
        color: var(--marvel-red);
        border-left: 5px solid var(--marvel-red);
        padding-left: 1rem;
    }
    
    .header-dc {
        color: var(--dc-blue);
        border-left: 5px solid var(--dc-blue);
        padding-left: 1rem;
    }
    
    .metric-marvel {
        border-left: 4px solid var(--marvel-red) !important;
    }
    
    .metric-dc {
        border-left: 4px solid var(--dc-blue) !important;
    }
    
    .winner-section {
        background: #FFF9C4;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid #FFD600;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div style="text-align:center; margin-bottom:2rem;">
    <h1 style="font-size:2.5rem;">🦸 MARVEL vs DC 🦇</h1>
    <h3>Análise Financeira de Filmes (2004-2019)</h3>
    <p style="color:var(--neutral);">Baseado em dados reais de orçamento e bilheteria</p>
</div>
""", unsafe_allow_html=True)

# Função para detectar outliers
def detect_outliers(df, column='ROI'):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    df['Outlier'] = df[column].apply(
        lambda x: 'Outlier' if (x < lower_bound) or (x > upper_bound) else 'Normal'
    )
    return df

# Carregar dados
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('db.csv')
    except:
        # Dados de fallback (mesmo conteúdo do CSV)
        data = [
            ["Iron Man","Marvel",7.9,79,126,2008,140000000,98618668,318604126,585366247],
            # ... (todos os outros filmes)
            ["Joker","DC",8.7,59,122,2019,55000000,96202337,333204580,1060504580]
        ]
        df = pd.DataFrame(data, columns=[
            'Original Title','Company','Rate','Metascore','Minutes','Release',
            'Budget','Opening Weekend USA','Gross USA','Gross Worldwide'
        ])
    
    # Processamento
    df = df.rename(columns={'Original Title': 'Original_Title', 'Gross Worldwide': 'Gross_Worldwide'})
    df['Budget'] = df['Budget'].astype(str).str.replace(' ', '').str.replace(',', '').astype(float)
    df['Gross_Worldwide'] = df['Gross_Worldwide'].astype(str).str.replace(' ', '').str.replace(',', '').astype(float)
    df['ROI'] = (df['Gross_Worldwide'] - df['Budget']) / df['Budget']
    
    # Categorias
    df['Budget_Category'] = pd.cut(df['Budget'], 
                                 bins=[0, 100e6, 200e6, float('inf')],
                                 labels=['Baixo (<$100M)', 'Médio ($100M-$200M)', 'Alto (>$200M)'])
    
    # Identificar sequências
    sequel_keywords = ['2', '3', 'II', 'III', 'Age of', 'Civil War', 'Dark World']
    df['Is_Sequel'] = df['Original_Title'].apply(lambda x: int(any(kw in str(x) for kw in sequel_keywords)))
    
    return df

df = load_data()
df = detect_outliers(df)

# Sidebar
st.sidebar.header("🔧 Controles")
companies = st.sidebar.multiselect(
    "Selecionar Franquias:",
    options=df['Company'].unique(),
    default=df['Company'].unique()
)

show_outliers = st.sidebar.checkbox("Mostrar outliers", value=True)

# Estatísticas rápidas na sidebar
marvel_count = len(df[df['Company'] == 'Marvel'])
dc_count = len(df[df['Company'] == 'DC'])
st.sidebar.markdown(f"""
**📊 Estatísticas:**
- Marvel: {marvel_count} filmes
- DC: {dc_count} filmes
- Período: {df['Release'].min()} - {df['Release'].max()}
""")

# Filtrar dados
if not companies:
    st.error("Selecione pelo menos uma franquia na sidebar")
    st.stop()

df_filtered = df[df['Company'].isin(companies)]
if not show_outliers:
    df_filtered = df_filtered[df_filtered['Outlier'] == 'Normal']

# Métricas principais
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Filmes", len(df_filtered))
with col2:
    st.metric("ROI Médio", f"{df_filtered['ROI'].mean():.1%}")
with col3:
    st.metric("Bilheteria Total", f"${df_filtered['Gross_Worldwide'].sum()/1e9:.1f}B")

# Análise por franquia
st.markdown("## 🏆 ROI por Franquia")
roi_stats = df_filtered.groupby('Company')['ROI'].agg(['mean', 'count']).sort_values('mean', ascending=False)
fig = px.bar(roi_stats, x=roi_stats.index, y='mean', color=roi_stats.index,
             color_discrete_map={'Marvel': '#ED1D24', 'DC': '#0078F0'})
st.plotly_chart(fig, use_container_width=True)

# Top filmes
st.markdown("## 🎬 Top Filmes por ROI")
top5 = df_filtered.nlargest(5, 'ROI')[['Original_Title', 'Company', 'ROI', 'Budget', 'Gross_Worldwide']]
bottom5 = df_filtered.nsmallest(5, 'ROI')[['Original_Title', 'Company', 'ROI', 'Budget', 'Gross_Worldwide']]

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🏅 Melhores Performances")
    st.dataframe(top5.style.format({
        'ROI': '{:.1%}',
        'Budget': '${:,.0f}',
        'Gross_Worldwide': '${:,.0f}'
    }), hide_index=True)

with col2:
    st.markdown("### ⚠️ Piores Performances")
    st.dataframe(bottom5.style.format({
        'ROI': '{:.1%}',
        'Budget': '${:,.0f}',
        'Gross_Worldwide': '${:,.0f}'
    }), hide_index=True)

# Análise temporal
st.markdown("## 📈 Evolução do ROI ao Longo do Tempo")
temp_df = df_filtered.groupby(['Release', 'Company'])['ROI'].mean().reset_index()
fig = px.line(temp_df, x='Release', y='ROI', color='Company', 
              color_discrete_map={'Marvel': '#ED1D24', 'DC': '#0078F0'})
st.plotly_chart(fig, use_container_width=True)

# Vencedor
st.markdown("## 🏁 Vencedor")
marvel_roi = df[df['Company'] == 'Marvel']['ROI'].mean()
dc_roi = df[df['Company'] == 'DC']['ROI'].mean()

if marvel_roi > dc_roi:
    st.markdown(f"""
    <div class="winner-section">
        <h2 style="color:var(--marvel-red);">MARVEL VENCE!</h2>
        <p>ROI médio: {marvel_roi:.1%} vs DC: {dc_roi:.1%}</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="winner-section">
        <h2 style="color:var(--dc-blue);">DC VENCE!</h2>
        <p>ROI médio: {dc_roi:.1%} vs Marvel: {marvel_roi:.1%}</p>
    </div>
    """, unsafe_allow_html=True)

# Detalhes técnicos
st.markdown("---")
st.markdown("""
**📝 Notas Metodológicas:**
- ROI calculado como: (Bilheteria Mundial - Orçamento) / Orçamento
- Dados coletados de fontes públicas (IMDB, Box Office Mojo)
- Análise considera {len(df)} filmes (Marvel: {marvel_count}, DC: {dc_count})
""".format(len(df)=len(df), marvel_count=marvel_count, dc_count=dc_count))
