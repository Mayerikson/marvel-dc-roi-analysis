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

# Carregar dados reais
@st.cache_data
def load_data():
    try:
        # Tentativas múltiplas de codificação
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv('db.csv', encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise Exception("Não foi possível ler o arquivo com nenhuma codificação testada")
            
    except (FileNotFoundError, Exception) as e:
        st.warning(f"Problema ao carregar 'db.csv': {str(e)}. Usando dados de exemplo.")
        # Dados reais do CSV como fallback
        data = [
            ["Iron Man","Marvel",7.9,79,126,2008,140000000,98618668,318604126,585366247],
            ["The Incredible Hulk","Marvel",6.7,61,112,2008,150000000,55414050,134806913,263427551],
            ["Iron Man 2","Marvel",7,57,124,2010,200000000,128122480,312433331,623933331],
            ["Thor","Marvel",7,57,115,2011,150000000,65723338,181030624,449326618],
            ["Captain America: The First Avenger","Marvel",6.9,66,124,2011,140000000,65058524,176654505,370569774],
            ["The Avengers","Marvel",8,69,143,2012,220000000,207438708,623357910,1518812988],
            ["Iron Man Three","Marvel",7.2,62,130,2013,200000000,174144585,409013994,1214811252],
            ["Thor: The Dark World","Marvel",6.9,54,112,2013,170000000,85737841,206362140,644783140],
            ["Captain America: The Winter Soldier","Marvel",7.7,70,136,2014,170000000,95023721,259766572,714421503],
            ["Guardians of the Galaxy","Marvel",8,76,121,2014,170000000,94320883,333176600,772776600],
            ["Avengers: Age of Ultron","Marvel",7.3,66,141,2015,250000000,191271109,459005868,1402805868],
            ["Ant-Man","Marvel",7.3,64,117,2015,130000000,57225526,180202163,519311965],
            ["Captain America: Civil War","Marvel",7.8,75,147,2016,250000000,179139142,408084349,1153296293],
            ["Doctor Strange","Marvel",7.5,72,115,2016,165000000,85058311,232641920,677718395],
            ["Guardians of the Galaxy Vol. 2","Marvel",7.6,67,136,2017,200000000,146510104,389813101,863756051],
            ["Spider-Man: Homecoming","Marvel",7.4,73,133,2017,175000000,117027503,334201140,880166924],
            ["Thor:Ragnarok","Marvel",7.9,74,130,2017,180000000,122744989,315058289,853977126],
            ["Black Panther","Marvel",7.3,88,134,2018,200000000,202003951,700059566,1346913161],
            ["Avengers: Infinity War","Marvel",8.5,68,149,2018,321000000,257698183,678815482,2048359754],
            ["Ant-Man and the Wasp","Marvel",7.1,70,118,2018,162000000,75812205,216648740,622674139],
            ["Captain Marve","Marvel",6.9,64,123,2019,175000000,153433423,426829839,1128274794],
            ["Avengers: Endgame","Marvel",8.5,78,181,2019,356000000,357115007,858373000,2797800564],
            ["Spider-Man: Far from Home","Marvel",7.6,69,129,2019,160000000,92579212,390532085,1131927996],
            ["Catwoman","DC",3.3,27,104,2004,100000000,16728411,40202379,82102379],
            ["Batman Begins","DC",8.2,70,140,2005,150000000,48745440,206852432,373413297],
            ["Superman Returns","DC",6,72,154,2006,270000000,52535096,200081192,391081192],
            ["The Dark Knight","DC",9,84,152,2008,185000000,158411483,535234033,1004934033],
            ["Watchmen","DC",7.6,56,162,2009,130000000,55214334,107509799,185258983],
            ["Jonah Hex","DC",4.7,33,81,2010,47000000,5379365,10547117,10903312],
            ["Green Lantern","DC",5.5,39,114,2011,200000000,53174303,116601172,219851172],
            ["The Dark Knight Rises","DC",8.4,78,164,2012,250000000,160887295,448139099,1081041287],
            ["Man of Steel","DC",7.1,55,143,2013,225000000,116619362,291045518,668045518],
            ["Batman v Superman: Dawn of Justice","DC",6.5,44,151,2016,250000000,166007347,330360194,873634919],
            ["Suicide Squad","DC",6,40,123,2016,175000000,133682248,325100054,746846894],
            ["Wonder Woman","DC",7.4,76,141,2017,149000000,103251471,412563408,821847012],
            ["Justice League","DC",6.4,45,120,2017,300000000,93842239,229024295,657924295],
            ["Aquaman","DC",7,55,143,2018,160000000,67873522,335061807,1148161807],
            ["Shazam!","DC",7.1,71,132,2019,100000000,53505326,140371656,364571656],
            ["Joker","DC",8.7,59,122,2019,55000000,96202337,333204580,1060504580]
        ]
        
        df = pd.DataFrame(data, columns=[
            'Original Title','Company','Rate','Metascore','Minutes','Release',
            'Budget','Opening Weekend USA','Gross USA','Gross Worldwide'
        ])
    
    # Limpeza e processamento dos dados
    # Remover espaços extras e caracteres inválidos
    for col in ['Budget', 'Gross Worldwide']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(' ', '').str.replace(',', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Renomear colunas para padronização
    column_mapping = {
        'Original Title': 'Original_Title',
        'Gross Worldwide': 'Gross_Worldwide'
    }
    df = df.rename(columns=column_mapping)
    
    # Calcular ROI
    df['ROI'] = (df['Gross_Worldwide'] - df['Budget']) / df['Budget']
    
    # Identificar sequências/continuações
    sequel_indicators = ['2', '3', 'II', 'III', 'Age of', 'Civil War', 'Endgame', 'Infinity', 
                        'v Superman', 'Dark World', 'Winter Soldier', 'Ragnarok', 'Returns',
                        'Rises', 'Dawn of Justice']
    
    df['Is_Sequel'] = df['Original_Title'].apply(
        lambda x: 1 if any(indicator in str(x) for indicator in sequel_indicators) else 0
    )
    
    # Categorias de orçamento
    df['Budget_Category'] = pd.cut(df['Budget'], 
                                 bins=[0, 100_000_000, 200_000_000, float('inf')],
                                 labels=['Baixo (< $100M)', 'Médio ($100M-200M)', 'Alto (> $200M)'])
    
    df['Movie_Type'] = df['Is_Sequel'].apply(lambda x: 'Sequência/Continuação' if x else 'Filme de Origem')
    
    # Remover linhas com dados faltantes essenciais
    df = df.dropna(subset=['Budget', 'Gross_Worldwide', 'ROI'])
    
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

# ANÁLISE DE OUTLIERS
st.markdown('<div class="question-header">🎯 ANÁLISE DE OUTLIERS: O que são e por que excluí-los?</div>', unsafe_allow_html=True)

# Identificar outliers
outliers_df = df[df['Outlier'] == 'Outlier'].copy()
normal_df = df[df['Outlier'] == 'Normal'].copy()

if len(outliers_df) > 0:
    st.markdown("""
    ### 🔍 **O que são Outliers?**
    Outliers são valores que se distanciam significativamente do padrão dos demais dados. 
    No contexto de ROI, são filmes com performance financeira **extremamente alta ou baixa** 
    comparado à média geral.
    
    ### 📊 **Como identificamos?**
    Usamos o método IQR (Interquartile Range):
    - **Q1**: 25% dos dados (1º quartil)
    - **Q3**: 75% dos dados (3º quartil) 
    - **IQR**: Q3 - Q1
    - **Outliers**: Valores abaixo de Q1 - 1.5×IQR ou acima de Q3 + 1.5×IQR
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 **OUTLIERS POSITIVOS** (Super Sucessos)")
        positive_outliers = outliers_df[outliers_df['ROI'] > df['ROI'].quantile(0.75)]
        if len(positive_outliers) > 0:
            pos_display = positive_outliers[['Original_Title', 'Company', 'ROI', 'Budget', 'Gross_Worldwide']].copy()
            pos_display['ROI'] = pos_display['ROI'].apply(lambda x: f"{x:.1%}")
            pos_display['Budget'] = pos_display['Budget'].apply(lambda x: f"${x/1e6:.0f}M")
            pos_display['Gross_Worldwide'] = pos_display['Gross_Worldwide'].apply(lambda x: f"${x/1e6:.0f}M")
            st.dataframe(pos_display, hide_index=True)
            
            st.markdown("**Por que são outliers:**")
            for _, film in positive_outliers.iterrows():
                st.write(f"• **{film['Original_Title']}**: ROI de {film['ROI']:.1%} - Performance excepcional!")
        else:
            st.write("Nenhum outlier positivo identificado")
    
    with col2:
        st.subheader("📉 **OUTLIERS NEGATIVOS** (Grandes Fracassos)")
        negative_outliers = outliers_df[outliers_df['ROI'] < df['ROI'].quantile(0.25)]
        if len(negative_outliers) > 0:
            neg_display = negative_outliers[['Original_Title', 'Company', 'ROI', 'Budget', 'Gross_Worldwide']].copy()
            neg_display['ROI'] = neg_display['ROI'].apply(lambda x: f"{x:.1%}")
            neg_display['Budget'] = neg_display['Budget'].apply(lambda x: f"${x/1e6:.0f}M")
            neg_display['Gross_Worldwide'] = neg_display['Gross_Worldwide'].apply(lambda x: f"${x/1e6:.0f}M")
            st.dataframe(neg_display, hide_index=True)
            
            st.markdown("**Por que são outliers:**")
            for _, film in negative_outliers.iterrows():
                st.write(f"• **{film['Original_Title']}**: ROI de {film['ROI']:.1%} - Performance muito abaixo do esperado")
        else:
            st.write("Nenhum outlier negativo identificado")
    
    # Estatísticas dos outliers
    st.markdown("### 📈 **Impacto dos Outliers nas Médias**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "ROI com Outliers", 
            f"{df['ROI'].mean():.1%}",
            f"{(df['ROI'].mean() - normal_df['ROI'].mean()):.1%}"
        )
    
    with col2:
        st.metric(
            "ROI sem Outliers", 
            f"{normal_df['ROI'].mean():.1%}",
            "Mais estável"
        )
    
    with col3:
        st.metric(
            "Total de Outliers", 
            f"{len(outliers_df)} filmes",
            f"{len(outliers_df)/len(df)*100:.1f}% do dataset"
        )
    
    # Razões para excluir outliers
    st.markdown("""
    ### 🎯 **Por que excluir Outliers na análise?**
    
    **✅ Argumentos A FAVOR da exclusão:**
    - **Análise mais representativa**: Remove casos extremos que distorcem a média
    - **Comparação mais justa**: Avalia a capacidade consistente de cada franquia
    - **Estratégia de negócios**: Foca na performance "típica" esperada
    - **Reduz variabilidade**: Estatísticas mais estáveis e confiáveis
    
    **❌ Argumentos CONTRA a exclusão:**
    - **Capacidade de criar sucessos**: Blockbusters fazem parte da estratégia
    - **Realidade do mercado**: Sucessos extremos geram muito lucro
    - **Gestão de risco**: Importante avaliar tanto sucessos quanto fracassos
    - **Completude dos dados**: Todos os filmes fazem parte da história
    
    **🔧 Use o filtro acima para alternar entre as duas análises e tire suas próprias conclusões!**
    """)

else:
    st.markdown("""
    ### 📊 **Nenhum Outlier Detectado**
    
    Usando o método IQR (Interquartile Range), não foram identificados outliers significativos 
    nos dados de ROI. Isso significa que todos os filmes têm performance dentro do padrão 
    estatisticamente esperado.
    
    **Possíveis razões:**
    - Dataset pequeno (39 filmes)
    - Distribuição relativamente uniforme dos ROIs
    - Critério IQR pode ser conservador para este dataset
    
    💡 **Dica**: Mesmo sem outliers estatísticos, você pode observar filmes com ROI 
    muito alto ou baixo nas tabelas "TOP 5" e "BOTTOM 5" acima.
    """)

# Estatísticas do dataset
st.markdown('<div class="question-header">📈 Estatísticas do Dataset</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    marvel_count = len(df[df['Company'] == 'Marvel'])
    dc_count = len(df[df['Company'] == 'DC'])
    st.metric("Total Marvel", marvel_count)
    st.metric("Total DC", dc_count)

with col2:
    year_range = f"{df['Release'].min()} - {df['Release'].max()}"
    st.metric("Período", year_range)
    avg_budget = df['Budget'].mean()
    st.metric("Orçamento Médio", f"${avg_budget/1e6:.0f}M")

with col3:
    highest_roi = df.loc[df['ROI'].idxmax()]
    lowest_roi = df.loc[df['ROI'].idxmin()]
    st.metric("Maior ROI", f"{highest_roi['Original_Title']} ({highest_roi['ROI']:.1%})")
    st.metric("Menor ROI", f"{lowest_roi['Original_Title']} ({lowest_roi['ROI']:.1%})")

# Insights finais
st.markdown('<div class="insight-text">📊 Análise baseada em dados reais de ROI (Retorno sobre Investimento) de filmes Marvel e DC. ROI = (Receita Mundial - Orçamento) / Orçamento. Dataset com 39 filmes desde 2004.</div>', unsafe_allow_html=True)
