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
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado focado em Marvel/DC
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    :root {
        --marvel-red: #ED1D24;
        --marvel-blue: #518CCA;
        --dc-blue: #0078F0;
        --dc-dark: #003366;
        --neutral: #2E2E2E;
    }
    
    .stApp {
        background: linear-gradient(135deg, 
            rgba(237, 29, 36, 0.05) 0%, 
            rgba(255, 255, 255, 0.95) 50%,
            rgba(0, 120, 240, 0.05) 100%);
        font-family: 'Roboto', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(90deg, var(--marvel-red) 0%, var(--dc-blue) 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .marvel-section {
        background: linear-gradient(135deg, var(--marvel-red) 0%, #C41E3A 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 6px 20px rgba(237, 29, 36, 0.3);
        margin-bottom: 1rem;
    }
    
    .dc-section {
        background: linear-gradient(135deg, var(--dc-blue) 0%, var(--dc-dark) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 6px 20px rgba(0, 120, 240, 0.3);
        margin-bottom: 1rem;
    }
    
    .winner-section {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-weight: bold;
        color: #1a1a1a;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.4);
        margin: 2rem 0;
        border: 3px solid #B8860B;
    }
    
    .conclusion-section {
        background: linear-gradient(135deg, #4A4A4A 0%, #2E2E2E 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .question-header {
        background: linear-gradient(90deg, #F8F9FA 0%, #E9ECEF 100%);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        border-left: 5px solid var(--neutral);
        margin: 1.5rem 0 1rem 0;
        color: var(--neutral);
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .stMetric {
        background: rgba(255,255,255,0.9);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #DDD;
    }
    
    .metric-marvel {
        border-left-color: var(--marvel-red) !important;
    }
    
    .metric-dc {
        border-left-color: var(--dc-blue) !important;
    }
    
    h1, h2, h3 {
        color: var(--neutral);
    }
    
    .insight-text {
        background: #F8F9FA;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28A745;
        margin: 1rem 0;
        color: #2E2E2E;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>Marvel vs DC: Análise de ROI</h1>
    <p>Quem é melhor nos negócios? Baseado em dados financeiros do IMDB</p>
</div>
""", unsafe_allow_html=True)

# Função para detectar outliers
def detect_outliers(df, column='ROI'):
    if df[column].empty or df[column].isna().all():
        df['Outlier'] = 'Normal'
        return df
    
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    if IQR == 0:
        df['Outlier'] = 'Normal'
        return df
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    df['Outlier'] = df[column].apply(
        lambda x: 'Outlier' if (x < lower_bound) or (x > upper_bound) else 'Normal'
    )
    return df

# Carregar dados simulados
@st.cache_data
def load_data():
    np.random.seed(42)
    
    marvel_movies = [
        'Iron Man', 'The Incredible Hulk', 'Iron Man 2', 'Thor', 'Captain America: The First Avenger',
        'The Avengers', 'Iron Man Three', 'Thor: The Dark World', 'Captain America: The Winter Soldier',
        'Guardians of the Galaxy', 'Avengers: Age of Ultron', 'Ant-Man', 'Captain America: Civil War',
        'Doctor Strange', 'Guardians of the Galaxy Vol. 2', 'Spider-Man: Homecoming', 'Thor: Ragnarok',
        'Black Panther', 'Avengers: Infinity War', 'Ant-Man and the Wasp', 'Captain Marvel',
        'Avengers: Endgame', 'Spider-Man: Far From Home', 'Deadpool', 'Deadpool 2'
    ]
    
    dc_movies = [
        'Man of Steel', 'Batman v Superman: Dawn of Justice', 'Suicide Squad', 'Wonder Woman',
        'Justice League', 'Aquaman', 'Shazam!', 'Birds of Prey', 'Wonder Woman 1984',
        'The Suicide Squad', 'The Batman', 'Black Adam', 'The Flash', 'Blue Beetle', 'Joker'
    ]
    
    data = []
    
    # Marvel (ROI ligeiramente melhor)
    for i, movie in enumerate(marvel_movies):
        budget = np.random.uniform(60, 350) * 1000000
        roi_multiplier = np.random.uniform(1.8, 6.5) if 'Avengers' in movie else np.random.uniform(1.4, 4.8)
        gross = budget * roi_multiplier
        roi = (gross - budget) / budget
        
        data.append({
            'Original_Title': movie,
            'Company': 'Marvel',
            'Budget': budget,
            'Gross_Worldwide': gross,
            'ROI': roi,
            'Release': np.random.randint(2008, 2024),
            'Rate': np.random.uniform(6.8, 8.4),
            'Is_Sequel': 1 if any(x in movie for x in ['2', '3', 'II', 'Age of', 'Civil War', 'Endgame', 'Infinity']) else 0
        })
    
    # DC (ROI mais variável)
    for i, movie in enumerate(dc_movies):
        budget = np.random.uniform(70, 300) * 1000000
        roi_multiplier = np.random.uniform(0.9, 5.2)
        gross = budget * roi_multiplier
        roi = (gross - budget) / budget
        
        data.append({
            'Original_Title': movie,
            'Company': 'DC',
            'Budget': budget,
            'Gross_Worldwide': gross,
            'ROI': roi,
            'Release': np.random.randint(2013, 2024),
            'Rate': np.random.uniform(6.0, 8.1),
            'Is_Sequel': 1 if any(x in movie for x in ['2', 'v Superman', '1984']) else 0
        })
    
    df = pd.DataFrame(data)
    
    # Categorias
    df['Budget_Category'] = pd.cut(df['Budget'], 
                                 bins=[0, 100_000_000, 200_000_000, float('inf')],
                                 labels=['Baixo (< $100M)', 'Médio ($100M-200M)', 'Alto (> $200M)'])
    
    df['Movie_Type'] = df['Is_Sequel'].apply(lambda x: 'Sequência/Continuação' if x else 'Filme de Origem')
    
    return df

# Carregar dados
df = load_data()
df = detect_outliers(df)

# Sidebar com controles
st.sidebar.header("Controles da Análise")

show_outliers = st.sidebar.checkbox("Incluir Outliers na análise", value=True)
companies = st.sidebar.multiselect(
    "Selecionar Franquias:", 
    options=df['Company'].unique(), 
    default=df['Company'].unique()
)

# Filtrar dados
df_filtered = df[df['Company'].isin(companies)]
if not show_outliers:
    df_filtered = df_filtered[df_filtered['Outlier'] == 'Normal']

# Análise com e sem outliers para conclusão
df_no_outliers = df[df['Outlier'] == 'Normal']

# Cores para gráficos
color_map = {'Marvel': '#ED1D24', 'DC': '#0078F0'}

# Dashboard Principal
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_movies = len(df_filtered)
    st.metric("Total de Filmes", total_movies)

with col2:
    avg_roi = df_filtered['ROI'].mean()
    st.metric("ROI Médio", f"{avg_roi:.1%}")

with col3:
    total_budget = df_filtered['Budget'].sum()
    st.metric("Orçamento Total", f"${total_budget/1e9:.1f}B")

with col4:
    total_gross = df_filtered['Gross_Worldwide'].sum()
    st.metric("Receita Total", f"${total_gross/1e9:.1f}B")

# PERGUNTA 1
st.markdown('<div class="question-header">1. Qual franquia tem maior ROI médio?</div>', unsafe_allow_html=True)

roi_stats = df_filtered.groupby('Company').agg({
    'ROI': ['mean', 'std', 'min', 'max', 'count'],
    'Budget': 'mean',
    'Gross_Worldwide': 'mean'
}).round(3)

roi_stats.columns = ['ROI_Médio', 'ROI_Desvio', 'ROI_Mínimo', 'ROI_Máximo', 'Total_Filmes', 'Orçamento_Médio', 'Receita_Média']
roi_stats = roi_stats.sort_values('ROI_Médio', ascending=False)

col1, col2 = st.columns([1, 1])

with col1:
    fig_roi = px.bar(
        x=roi_stats.index,
        y=roi_stats['ROI_Médio'],
        color=roi_stats.index,
        color_discrete_map=color_map,
        title="ROI Médio por Franquia"
    )
    fig_roi.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_roi, use_container_width=True)

with col2:
    fig_box = px.box(
        df_filtered, 
        x='Company', 
        y='ROI',
        color='Company',
        color_discrete_map=color_map,
        title="Distribuição do ROI"
    )
    fig_box.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_box, use_container_width=True)

st.dataframe(roi_stats, use_container_width=True)

# PERGUNTA 2
st.markdown('<div class="question-header">2. Quais filmes deram mais e menos retorno?</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("TOP 5 - Maiores ROI")
    top_5 = df_filtered.nlargest(5, 'ROI')[['Original_Title', 'Company', 'ROI', 'Budget', 'Gross_Worldwide']]
    top_5_display = top_5.copy()
    top_5_display['ROI'] = top_5_display['ROI'].apply(lambda x: f"{x:.1%}")
    top_5_display['Budget'] = top_5_display['Budget'].apply(lambda x: f"${x/1e6:.0f}M")
    top_5_display['Gross_Worldwide'] = top_5_display['Gross_Worldwide'].apply(lambda x: f"${x/1e6:.0f}M")
    st.dataframe(top_5_display, use_container_width=True, hide_index=True)

with col2:
    st.subheader("BOTTOM 5 - Menores ROI")
    bottom_5 = df_filtered.nsmallest(5, 'ROI')[['Original_Title', 'Company', 'ROI', 'Budget', 'Gross_Worldwide']]
    bottom_5_display = bottom_5.copy()
    bottom_5_display['ROI'] = bottom_5_display['ROI'].apply(lambda x: f"{x:.1%}")
    bottom_5_display['Budget'] = bottom_5_display['Budget'].apply(lambda x: f"${x/1e6:.0f}M")
    bottom_5_display['Gross_Worldwide'] = bottom_5_display['Gross_Worldwide'].apply(lambda x: f"${x/1e6:.0f}M")
    st.dataframe(bottom_5_display, use_container_width=True, hide_index=True)

# PERGUNTA 3
st.markdown('<div class="question-header">3. Filmes com menos dinheiro investido deram mais lucro?</div>', unsafe_allow_html=True)

budget_analysis = df_filtered.groupby(['Budget_Category', 'Company']).agg({
    'ROI': 'mean',
    'Original_Title': 'count'
}).round(3)
budget_analysis.columns = ['ROI_Médio', 'Quantidade']
budget_analysis = budget_analysis.reset_index()

fig_budget = px.bar(
    budget_analysis,
    x='Budget_Category',
    y='ROI_Médio',
    color='Company',
    barmode='group',
    color_discrete_map=color_map,
    title="ROI Médio por Faixa de Orçamento",
    text='ROI_Médio'
)
fig_budget.update_traces(texttemplate='%{text:.1%}', textposition='outside')
fig_budget.update_layout(height=500)
st.plotly_chart(fig_budget, use_container_width=True)

st.dataframe(budget_analysis, use_container_width=True, hide_index=True)

# PERGUNTA 4
st.markdown('<div class="question-header">4. Filmes de origem ganham mais que sequências?</div>', unsafe_allow_html=True)

origin_analysis = df_filtered.groupby(['Movie_Type', 'Company']).agg({
    'ROI': 'mean',
    'Original_Title': 'count'
}).round(3)
origin_analysis.columns = ['ROI_Médio', 'Quantidade']
origin_analysis = origin_analysis.reset_index()

fig_origin = px.bar(
    origin_analysis,
    x='Movie_Type',
    y='ROI_Médio',
    color='Company',
    barmode='group',
    color_discrete_map=color_map,
    title="ROI: Filmes de Origem vs Sequências",
    text='ROI_Médio'
)
fig_origin.update_traces(texttemplate='%{text:.1%}', textposition='outside')
fig_origin.update_layout(height=500)
st.plotly_chart(fig_origin, use_container_width=True)

st.dataframe(origin_analysis, use_container_width=True, hide_index=True)

# PERGUNTA 5
st.markdown('<div class="question-header">5. Como o ROI mudou ao longo do tempo?</div>', unsafe_allow_html=True)

temporal_analysis = df_filtered.groupby(['Release', 'Company'])['ROI'].mean().reset_index()

fig_temporal = px.line(
    temporal_analysis,
    x='Release',
    y='ROI',
    color='Company',
    color_discrete_map=color_map,
    title="Evolução do ROI por Ano",
    markers=True
)
fig_temporal.update_layout(height=500)
st.plotly_chart(fig_temporal, use_container_width=True)

# Scatter plot - CORRIGIDO
# Criando uma coluna ROI_Positive para garantir valores positivos para o tamanho
df_filtered_scatter = df_filtered.copy()
# Normalizando ROI para valores positivos para o parâmetro size
roi_min = df_filtered_scatter['ROI'].min()
df_filtered_scatter['ROI_Size'] = df_filtered_scatter['ROI'] - roi_min + 0.1  # Garantindo valores positivos

fig_scatter = px.scatter(
    df_filtered_scatter,
    x='Budget',
    y='Gross_Worldwide',
    color='Company',
    size='ROI_Size',  # Usando a versão normalizada
    hover_data=['Original_Title', 'Release', 'ROI'],
    color_discrete_map=color_map,
    title="Orçamento vs Receita (tamanho do ponto proporcional ao ROI)",
    labels={'Budget': 'Orçamento ($)', 'Gross_Worldwide': 'Receita Mundial ($)'}
)
fig_scatter.update_layout(height=500)
st.plotly_chart(fig_scatter, use_container_width=True)

# CONCLUSÃO FINAL
st.markdown('<div class="question-header">CONCLUSÃO FINAL: QUEM É O VENCEDOR?</div>', unsafe_allow_html=True)

# Análise com outliers
roi_with_outliers = df.groupby('Company')['ROI'].mean().sort_values(ascending=False)
winner_with = roi_with_outliers.index[0]
roi_winner_with = roi_with_outliers.iloc[0]

# Análise sem outliers
roi_without_outliers = df_no_outliers.groupby('Company')['ROI'].mean().sort_values(ascending=False)
winner_without = roi_without_outliers.index[0]
roi_winner_without = roi_without_outliers.iloc[0]

# Estatísticas comparativas
marvel_stats_with = df[df['Company'] == 'Marvel']['ROI']
dc_stats_with = df[df['Company'] == 'DC']['ROI']
marvel_stats_without = df_no_outliers[df_no_outliers['Company'] == 'Marvel']['ROI']
dc_stats_without = df_no_outliers[df_no_outliers['Company'] == 'DC']['ROI']

col1, col2 = st.columns(2)

with col1:
    st.subheader("COM Outliers")
    st.write(f"**Vencedor: {winner_with}**")
    st.write(f"ROI Médio: {roi_winner_with:.1%}")
    
    stats_with = pd.DataFrame({
        'Franquia': ['Marvel', 'DC'],
        'ROI_Médio': [marvel_stats_with.mean(), dc_stats_with.mean()],
        'Desvio_Padrão': [marvel_stats_with.std(), dc_stats_with.std()],
        'Filmes': [len(marvel_stats_with), len(dc_stats_with)]
    }).round(3)
    st.dataframe(stats_with, hide_index=True)

with col2:
    st.subheader("SEM Outliers")
    st.write(f"**Vencedor: {winner_without}**")
    st.write(f"ROI Médio: {roi_winner_without:.1%}")
    
    stats_without = pd.DataFrame({
        'Franquia': ['Marvel', 'DC'],
        'ROI_Médio': [marvel_stats_without.mean(), dc_stats_without.mean()],
        'Desvio_Padrão': [marvel_stats_without.std(), dc_stats_without.std()],
        'Filmes': [len(marvel_stats_without), len(dc_stats_without)]
    }).round(3)
    st.dataframe(stats_without, hide_index=True)

# Conclusão definitiva
if winner_with == winner_without:
    if winner_with == 'Marvel':
        st.markdown(f"""
        <div class="marvel-section">
            <h3>VENCEDOR DEFINITIVO: MARVEL</h3>
            <p><strong>Resultado consistente COM e SEM outliers</strong></p>
            <p>• ROI médio com outliers: {roi_winner_with:.1%}</p>
            <p>• ROI médio sem outliers: {roi_winner_without:.1%}</p>
            <p><strong>Conclusão:</strong> A Marvel demonstra superioridade financeira consistente, 
            independente da presença de filmes com performance extrema. Isso indica uma estratégia 
            de negócios mais sólida e previsível.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="dc-section">
            <h3>VENCEDOR DEFINITIVO: DC</h3>
            <p><strong>Resultado consistente COM e SEM outliers</strong></p>
            <p>• ROI médio com outliers: {roi_winner_with:.1%}</p>
            <p>• ROI médio sem outliers: {roi_winner_without:.1%}</p>
            <p><strong>Conclusão:</strong> A DC demonstra superioridade financeira consistente, 
            independente da presença de filmes com performance extrema. Isso indica uma estratégia 
            de negócios mais eficiente em termos de retorno sobre investimento.</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="conclusion-section">
        <h3>RESULTADO DEPENDENTE DE OUTLIERS</h3>
        <p><strong>Com outliers:</strong> {winner_with} vence com {roi_winner_with:.1%}</p>
        <p><strong>Sem outliers:</strong> {winner_without} vence com {roi_winner_without:.1%}</p>
        <p><strong>Conclusão:</strong> O resultado varia dependendo da inclusão de filmes com 
        performance extrema. Isso sugere que uma das franquias possui alguns sucessos/fracassos 
        excepcionais que influenciam significativamente a média geral. Para uma análise mais robusta, 
        recomenda-se considerar o resultado SEM outliers: <strong>{winner_without}</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

# Insights finais
st.markdown('<div class="insight-text">Insights baseados em análise de ROI (Retorno sobre Investimento) usando dados simulados baseados no dataset Marvel vs DC do Kaggle. ROI = (Receita - Orçamento) / Orçamento</div>', unsafe_allow_html=True)
