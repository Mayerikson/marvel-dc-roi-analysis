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
    page_title="🦸‍♂️ Marvel vs DC: Análise de ROI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado otimizado para cloud
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400;500;700&display=swap');
    
    :root {
        --marvel-red: #ED1D24;
        --marvel-blue: #518CCA;
        --dc-blue: #0078F0;
        --dc-gold: #FFD700;
        --hero-dark: #1E1E1E;
    }
    
    .stApp {
        background: linear-gradient(135deg, 
            rgba(237, 29, 36, 0.03) 0%, 
            rgba(255, 255, 255, 0.97) 50%,
            rgba(0, 120, 240, 0.03) 100%);
    }
    
    .main-header {
        background: linear-gradient(45deg, var(--marvel-red) 0%, var(--dc-blue) 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        font-family: 'Orbitron', monospace;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 0.5rem;
    }
    
    .marvel-card {
        background: linear-gradient(135deg, var(--marvel-red) 0%, #FF4757 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 25px rgba(237, 29, 36, 0.4);
        margin-bottom: 1rem;
    }
    
    .dc-card {
        background: linear-gradient(135deg, var(--dc-blue) 0%, #4A90E2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 25px rgba(0, 120, 240, 0.4);
        margin-bottom: 1rem;
    }
    
    .winner-card {
        background: linear-gradient(135deg, var(--dc-gold) 0%, #FFA500 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        color: var(--hero-dark);
        box-shadow: 0 12px 35px rgba(255, 215, 0, 0.6);
        margin: 1rem 0;
        font-family: 'Orbitron', monospace;
    }
    
    .insight-card {
        background: linear-gradient(135deg, #E8F5E8 0%, #F0FFF0 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: #2F4F2F;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(152, 251, 152, 0.3);
        border-left: 6px solid #00FF41;
    }
    
    .conclusion-card {
        background: linear-gradient(135deg, #8A2BE2 0%, #9932CC 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 15px 40px rgba(147, 112, 219, 0.5);
        font-family: 'Orbitron', monospace;
    }
    
    .stMetric {
        background: rgba(255,255,255,0.95);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid var(--dc-gold);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    h1, h2, h3 {
        font-family: 'Orbitron', monospace;
        color: var(--hero-dark);
    }
    
    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.8rem; }
        .marvel-card, .dc-card { padding: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🦸‍♂️ MARVEL vs DC: BATALHA DOS DADOS 🦸‍♀️</h1>
    <h3>Análise Estratégica de ROI com Insights Épicos</h3>
    <p><em>"Quando os números contam histórias heroicas!"</em></p>
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

# Carregar dados simulados otimizados
@st.cache_data
def load_data():
    """Carrega dados simulados baseados no dataset real Marvel vs DC"""
    
    np.random.seed(42)  # Para resultados consistentes
    
    # Dados baseados no dataset real do Kaggle
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
    
    # Gerar dados simulados mas realistas
    data = []
    
    # Marvel (geralmente ROI melhor)
    for i, movie in enumerate(marvel_movies):
        budget = np.random.uniform(50, 400) * 1000000  # 50M-400M
        # Marvel tende a ter ROI melhor
        roi_multiplier = np.random.uniform(1.5, 8.0) if 'Avengers' in movie else np.random.uniform(1.2, 5.0)
        gross = budget * roi_multiplier
        roi = (gross - budget) / budget
        
        data.append({
            'Original_Title': movie,
            'Company': 'Marvel',
            'Budget': budget,
            'Gross_Worldwide': gross,
            'ROI': roi,
            'Release': np.random.randint(2008, 2024),
            'Rate': np.random.uniform(6.5, 8.5),
            'Metascore': np.random.uniform(60, 90),
            'Runtime': np.random.randint(100, 180),
            'Genre': np.random.choice(['Action', 'Adventure', 'Sci-Fi']),
            'Is_Sequel': 1 if any(x in movie for x in ['2', '3', 'II', 'Age of', 'Civil War', 'Endgame', 'Infinity']) else 0
        })
    
    # DC (ROI mais variável)
    for i, movie in enumerate(dc_movies):
        budget = np.random.uniform(60, 350) * 1000000  # 60M-350M
        # DC tem mais variabilidade
        roi_multiplier = np.random.uniform(0.8, 6.0)
        gross = budget * roi_multiplier
        roi = (gross - budget) / budget
        
        data.append({
            'Original_Title': movie,
            'Company': 'DC',
            'Budget': budget,
            'Gross_Worldwide': gross,
            'ROI': roi,
            'Release': np.random.randint(2013, 2024),
            'Rate': np.random.uniform(5.5, 8.2),
            'Metascore': np.random.uniform(45, 85),
            'Runtime': np.random.randint(105, 185),
            'Genre': np.random.choice(['Action', 'Adventure', 'Fantasy']),
            'Is_Sequel': 1 if any(x in movie for x in ['2', 'v Superman', '1984']) else 0
        })
    
    df = pd.DataFrame(data)
    
    # Adicionar algumas categorias de orçamento
    df['Budget_Category'] = pd.cut(df['Budget'], 
                                 bins=[0, 100_000_000, 200_000_000, float('inf')],
                                 labels=['Baixo (< $100M)', 'Médio ($100M-200M)', 'Alto (> $200M)'])
    
    df['Movie_Type'] = df['Is_Sequel'].apply(lambda x: 'Sequência/Continuação' if x else 'Filme de Origem')
    
    return df

# Carregar dados
try:
    df = load_data()
    st.success(f"✅ Dataset carregado com sucesso! {len(df)} filmes analisados.")
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {str(e)}")
    st.stop()

# Detectar outliers
df = detect_outliers(df)

# Sidebar com controles
st.sidebar.header("🎛️ Controles da Análise")

# Filtros
companies = st.sidebar.multiselect(
    "🏢 Selecionar Franquias:", 
    options=df['Company'].unique(), 
    default=df['Company'].unique()
)

years = st.sidebar.slider(
    "📅 Período de Análise:",
    min_value=int(df['Release'].min()),
    max_value=int(df['Release'].max()),
    value=(int(df['Release'].min()), int(df['Release'].max()))
)

show_outliers = st.sidebar.checkbox("⚠️ Incluir Outliers", value=True)

# Filtrar dados
df_filtered = df[
    (df['Company'].isin(companies)) & 
    (df['Release'] >= years[0]) & 
    (df['Release'] <= years[1])
]

if not show_outliers:
    df_filtered = df_filtered[df_filtered['Outlier'] == 'Normal']

# Verificar se há dados após filtros
if df_filtered.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados!")
    st.stop()

# Dashboard Principal
col1, col2, col3, col4 = st.columns(4)

# Métricas principais
with col1:
    total_movies = len(df_filtered)
    st.metric("🎬 Total de Filmes", total_movies)

with col2:
    avg_roi = df_filtered['ROI'].mean()
    st.metric("📈 ROI Médio", f"{avg_roi:.1%}")

with col3:
    total_budget = df_filtered['Budget'].sum()
    st.metric("💰 Orçamento Total", f"${total_budget/1e9:.1f}B")

with col4:
    total_gross = df_filtered['Gross_Worldwide'].sum()
    st.metric("🌍 Receita Total", f"${total_gross/1e9:.1f}B")

# Análise principal
st.header("📊 Análise Comparativa: Marvel vs DC")

# Dividir em abas
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 ROI por Franquia", 
    "🎯 Top Filmes", 
    "💸 Orçamento vs Lucro", 
    "🎭 Origem vs Sequências", 
    "📈 Evolução Temporal"
])

with tab1:
    st.subheader("🏆 Qual franquia tem melhor ROI?")
    
    # Análise por empresa
    roi_by_company = df_filtered.groupby('Company').agg({
        'ROI': ['mean', 'std', 'min', 'max', 'count'],
        'Budget': 'mean',
        'Gross_Worldwide': 'mean'
    }).round(3)
    
    roi_by_company.columns = ['ROI_Médio', 'ROI_Desvio', 'ROI_Mínimo', 'ROI_Máximo', 'Total_Filmes', 'Orçamento_Médio', 'Receita_Média']
    roi_by_company = roi_by_company.sort_values('ROI_Médio', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras ROI médio
        fig_roi = px.bar(
            x=roi_by_company.index,
            y=roi_by_company['ROI_Médio'],
            color=roi_by_company.index,
            color_discrete_map={'Marvel': '#ED1D24', 'DC': '#0078F0'},
            title="ROI Médio por Franquia",
            labels={'x': 'Franquia', 'y': 'ROI Médio'}
        )
        fig_roi.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_roi, use_container_width=True)
    
    with col2:
        # Boxplot ROI
        fig_box = px.box(
            df_filtered, 
            x='Company', 
            y='ROI',
            color='Company',
            color_discrete_map={'Marvel': '#ED1D24', 'DC': '#0078F0'},
            title="Distribuição do ROI"
        )
        fig_box.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Determinar vencedor
    winner = roi_by_company.index[0]
    winner_roi = roi_by_company.iloc[0]['ROI_Médio']
    
    if winner == 'Marvel':
        st.markdown(f"""
        <div class="marvel-card">
            <h3>🏆 VENCEDOR: MARVEL</h3>
            <p><strong>ROI Médio: {winner_roi:.1%}</strong></p>
            <p>A Marvel demonstra consistência superior no retorno sobre investimento!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="dc-card">
            <h3>🏆 VENCEDOR: DC</h3>
            <p><strong>ROI Médio: {winner_roi:.1%}</strong></p>
            <p>A DC surpreende com melhor retorno sobre investimento!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabela detalhada
    st.subheader("📋 Estatísticas Detalhadas")
    st.dataframe(roi_by_company, use_container_width=True)

with tab2:
    st.subheader("🎯 Top Performances")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🥇 TOP 5 - Maiores ROI**")
        top_5 = df_filtered.nlargest(5, 'ROI')[['Original_Title', 'Company', 'ROI', 'Budget', 'Gross_Worldwide']]
        top_5['ROI'] = top_5['ROI'].apply(lambda x: f"{x:.1%}")
        top_5['Budget'] = top_5['Budget'].apply(lambda x: f"${x/1e6:.0f}M")
        top_5['Gross_Worldwide'] = top_5['Gross_Worldwide'].apply(lambda x: f"${x/1e6:.0f}M")
        st.dataframe(top_5, use_container_width=True, hide_index=True)
    
    with col2:
        st.write("**📉 BOTTOM 5 - Menores ROI**")
        bottom_5 = df_filtered.nsmallest(5, 'ROI')[['Original_Title', 'Company', 'ROI', 'Budget', 'Gross_Worldwide']]
        bottom_5['ROI'] = bottom_5['ROI'].apply(lambda x: f"{x:.1%}")
        bottom_5['Budget'] = bottom_5['Budget'].apply(lambda x: f"${x/1e6:.0f}M")
        bottom_5['Gross_Worldwide'] = bottom_5['Gross_Worldwide'].apply(lambda x: f"${x/1e6:.0f}M")
        st.dataframe(bottom_5, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("💸 Orçamento vs Lucratividade")
    
    # Análise por faixa de orçamento
    budget_analysis = df_filtered.groupby(['Budget_Category', 'Company']).agg({
        'ROI': 'mean',
        'Original_Title': 'count'
    }).round(3)
    budget_analysis.columns = ['ROI_Médio', 'Quantidade']
    budget_analysis = budget_analysis.reset_index()
    
    # Gráfico
    fig_budget = px.bar(
        budget_analysis,
        x='Budget_Category',
        y='ROI_Médio',
        color='Company',
        barmode='group',
        color_discrete_map={'Marvel': '#ED1D24', 'DC': '#0078F0'},
        title="ROI Médio por Faixa de Orçamento",
        text='ROI_Médio'
    )
    fig_budget.update_traces(texttemplate='%{text:.1%}', textposition='outside')
    fig_budget.update_layout(height=500)
    st.plotly_chart(fig_budget, use_container_width=True)
    
    # Insight
    low_budget_roi = budget_analysis[budget_analysis['Budget_Category'] == 'Baixo (< $100M)']['ROI_Médio'].mean()
    high_budget_roi = budget_analysis[budget_analysis['Budget_Category'] == 'Alto (> $200M)']['ROI_Médio'].mean()
    
    if low_budget_roi > high_budget_roi:
        st.markdown("""
        <div class="insight-card">
            <h3>💡 Insight: Menos é Mais!</h3>
            <p>Filmes com orçamento menor tendem a ter <strong>melhor ROI</strong>. 
            Isso sugere que criatividade e execução podem ser mais importantes que grandes investimentos!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="insight-card">
            <h3>💡 Insight: Investimento Compensa!</h3>
            <p>Filmes com orçamento maior conseguem <strong>melhor ROI</strong>. 
            Grandes investimentos em efeitos e marketing parecem compensar!</p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.subheader("🎭 Filmes de Origem vs Sequências")
    
    origin_analysis = df_filtered.groupby(['Movie_Type', 'Company']).agg({
        'ROI': 'mean',
        'Original_Title': 'count'
    }).round(3)
    origin_analysis.columns = ['ROI_Médio', 'Quantidade']
    origin_analysis = origin_analysis.reset_index()
    
    # Gráfico
    fig_origin = px.bar(
        origin_analysis,
        x='Movie_Type',
        y='ROI_Médio',
        color='Company',
        barmode='group',
        color_discrete_map={'Marvel': '#ED1D24', 'DC': '#0078F0'},
        title="ROI: Filmes de Origem vs Sequências",
        text='ROI_Médio'
    )
    fig_origin.update_traces(texttemplate='%{text:.1%}', textposition='outside')
    fig_origin.update_layout(height=500)
    st.plotly_chart(fig_origin, use_container_width=True)
    
    # Tabela
    st.dataframe(origin_analysis, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("📈 Evolução do ROI ao Longo do Tempo")
    
    # Análise temporal
    temporal_analysis = df_filtered.groupby(['Release', 'Company'])['ROI'].mean().reset_index()
    
    # Gráfico de linha
    fig_temporal = px.line(
        temporal_analysis,
        x='Release',
        y='ROI',
        color='Company',
        color_discrete_map={'Marvel': '#ED1D24', 'DC': '#0078F0'},
        title="Evolução do ROI por Ano",
        markers=True
    )
    fig_temporal.update_layout(height=500)
    st.plotly_chart(fig_temporal, use_container_width=True)
    
    # Scatter plot orçamento vs receita
    fig_scatter = px.scatter(
        df_filtered,
        x='Budget',
        y='Gross_Worldwide',
        color='Company',
        size='ROI',
        hover_data=['Original_Title', 'Release'],
        color_discrete_map={'Marvel': '#ED1D24', 'DC': '#0078F0'},
        title="Orçamento vs Receita (tamanho = ROI)",
        labels={'Budget': 'Orçamento ($)', 'Gross_Worldwide': 'Receita Mundial ($)'}
    )
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)

# Conclusão épica
st.markdown("""
<div class="conclusion-card">
    <h2>🎬 CONCLUSÃO ÉPICA</h2>
    <p><strong>Baseado na análise de dados de ROI, nossa batalha dos números revela insights fascinantes sobre o universo cinematográfico dos super-heróis!</strong></p>
    <p><em>"Os dados não mentem - mas eles contam histórias incríveis!" 🦸‍♂️📊</em></p>
</div>
""", unsafe_allow_html=True)

# Insights finais
st.subheader("🔍 Insights Principais da Análise")

insights = [
    f"🏆 **Vencedor ROI**: {winner} com ROI médio de {winner_roi:.1%}",
    f"🎬 **Total analisado**: {total_movies} filmes no período selecionado",
    f"💰 **Investimento total**: ${total_budget/1e9:.1f} bilhões em orçamentos",
    f"🌍 **Receita global**: ${total_gross/1e9:.1f} bilhões arrecadados mundialmente",
    f"📈 **ROI médio geral**: {avg_roi:.1%} de retorno sobre investimento"
]

for insight in insights:
    st.markdown(f"- {insight}")

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666; font-style: italic;">
    📊 Análise baseada em dados simulados do dataset Marvel vs DC | 
    🚀 Desenvolvido com Streamlit | 
    ⚡ Otimizado para deployment em nuvem
</div>
""", unsafe_allow_html=True)

# Sidebar com informações adicionais
st.sidebar.markdown("---")
st.sidebar.subheader("📋 Sobre a Análise")
st.sidebar.write("""
**Critério Principal**: ROI (Return on Investment)

**Fórmula**: ROI = (Receita - Orçamento) / Orçamento

**Dataset**: Baseado no Kaggle Marvel vs DC

**Período**: 2008-2024
""")

st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Configurações")
st.sidebar.write(f"**Filmes analisados**: {len(df_filtered)}")
st.sidebar.write(f"**Outliers**: {'Incluídos' if show_outliers else 'Excluídos'}")
st.sidebar.write(f"**Período**: {years[0]} - {years[1]}")

# Botão para download dos dados (opcional)
if st.sidebar.button("📥 Download Dados"):
    csv = df_filtered.to_csv(index=False)
    st.sidebar.download_button(
        label="Baixar CSV",
        data=csv,
        file_name=f"marvel_vs_dc_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
