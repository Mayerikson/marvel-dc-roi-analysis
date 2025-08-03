import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from sklearn.ensemble import IsolationForest
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Marvel vs DC: ROI Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #E23636 0%, #0078F0 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .marvel-card { background: linear-gradient(135deg, #E23636, #FF6B6B); }
    .dc-card { background: linear-gradient(135deg, #0078F0, #4A90E2); }
    .winner-card { background: linear-gradient(135deg, #FFD700, #FFA500); }
    .outlier-card { background: linear-gradient(135deg, #FF6347, #FF4500); }
    .stMetric { background: rgba(255, 255, 255, 0.9); }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    .winner-metric { animation: pulse 2s infinite; }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🎬 MARVEL vs DC: ROI ANALYSIS 🏆</h1>
    <h3>Análise com tratamento de outliers</h3>
</div>
""", unsafe_allow_html=True)

# Função para detectar outliers
def detect_outliers(df):
    model = IsolationForest(contamination=0.1, random_state=42)
    df['Outlier'] = model.fit_predict(df[['ROI']])
    df['Outlier'] = df['Outlier'].apply(lambda x: 'Outlier' if x == -1 else 'Normal')
    return df

# Carregar e preparar dados
@st.cache_data
def load_data():
    data = pd.read_csv('db.csv')  # Substitua pelo seu arquivo real
    
    # Verificar se 'Joker' está nos dados e marcar como outlier
    if 'Joker' in data['Original_Title'].values:
        data['Outlier'] = 'Normal'
        data.loc[data['Original_Title'] == 'Joker', 'Outlier'] = 'Outlier'
    else:
        data = detect_outliers(data)
    
    # Calcular ROI
    data['ROI'] = (data['Gross_Worldwide'] - data['Budget']) / data['Budget']
    
    # Classificar filmes
    sequel_keywords = ['2', '3', 'II', 'III', 'Age of', 'Civil War', 'Endgame', 'Infinity', 'v Superman']
    data['Tipo_Filme'] = data['Original_Title'].apply(
        lambda x: 'Sequência' if any(kw in str(x) for kw in sequel_keywords) else 'Origem'
    )
    
    # Faixa de orçamento
    data['Faixa_Orcamento'] = pd.cut(data['Budget'], 
                                   bins=[0, 100e6, 200e6, float('inf')],
                                   labels=['Baixo (<$100M)', 'Médio ($100M-$200M)', 'Alto (>$200M)'])
    return data

df = load_data()

# Sidebar com filtros
st.sidebar.header('🔍 Filtros Avançados')

# Opção para incluir/excluir outliers
include_outliers = st.sidebar.checkbox('Incluir outliers (como Joker)', value=False)

# Filtros principais
selected_companies = st.sidebar.multiselect(
    'Franquias',
    options=df['Company'].unique(),
    default=df['Company'].unique()
)

year_range = st.sidebar.slider(
    'Ano de Lançamento',
    min_value=int(df['Release'].min()),
    max_value=int(df['Release'].max()),
    value=(2008, 2023)
)

# Aplicar filtros
filtered_df = df[
    (df['Company'].isin(selected_companies)) &
    (df['Release'].between(year_range[0], year_range[1]))
]

if not include_outliers:
    filtered_df = filtered_df[filtered_df['Outlier'] == 'Normal']

# Métricas principais
st.header("📊 Métricas Principais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_roi = filtered_df['ROI'].mean()
    st.metric("ROI Médio", f"{avg_roi:.2f}")

with col2:
    total_movies = len(filtered_df)
    st.metric("Filmes Analisados", total_movies)

with col3:
    max_roi = filtered_df['ROI'].max()
    best_movie = filtered_df.loc[filtered_df['ROI'].idxmax(), 'Original_Title']
    st.metric("Maior ROI", f"{max_roi:.2f}", best_movie)

with col4:
    min_budget_high_roi = filtered_df[filtered_df['ROI'] > avg_roi]['Budget'].min()
    st.metric("Menor Orçamento com ROI Acima da Média", f"${min_budget_high_roi/1e6:.1f}M")

# Análise de Outliers
if not include_outliers and 'Outlier' in df.columns and df['Outlier'].value_counts().get('Outlier', 0) > 0:
    outliers = df[df['Outlier'] == 'Outlier']
    with st.expander("⚠️ Outliers Excluídos"):
        st.markdown("""
        <div class="outlier-card" style="padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3>Filmes identificados como outliers:</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for _, row in outliers.iterrows():
            st.markdown(f"""
            <div style="background: rgba(255,99,71,0.2); padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0;">
                <strong>{row['Original_Title']}</strong> (ROI: {row['ROI']:.2f})
            </div>
            """, unsafe_allow_html=True)
        
        st.write("Estes filmes foram excluídos da análise para evitar distorções.")

# Visualizações em abas
tab1, tab2, tab3 = st.tabs(["📈 ROI Comparativo", "💰 Orçamento vs Receita", "🎬 Detalhes por Filme"])

with tab1:
    st.header("Comparativo de ROI")
    
    # Gráfico de ROI por franquia
    fig1 = px.box(
        filtered_df,
        x='Company',
        y='ROI',
        color='Company',
        color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
        points="all",
        hover_data=['Original_Title', 'Release']
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Evolução temporal
    st.subheader("Evolução do ROI ao Longo dos Anos")
    fig2 = px.line(
        filtered_df.groupby(['Release', 'Company'])['ROI'].mean().reset_index(),
        x='Release',
        y='ROI',
        color='Company',
        markers=True,
        color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'}
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("Relação Orçamento vs Receita")
    
    # Gráfico de bolhas
    fig3 = px.scatter(
        filtered_df,
        x='Budget',
        y='Gross_Worldwide',
        size='ROI',
        color='Company',
        hover_name='Original_Title',
        log_x=True,
        log_y=True,
        color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
        trendline="lowess"
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # ROI por faixa de orçamento
    st.subheader("ROI Médio por Faixa de Orçamento")
    fig4 = px.bar(
        filtered_df.groupby('Faixa_Orcamento')['ROI'].mean().reset_index(),
        x='Faixa_Orcamento',
        y='ROI',
        color='ROI',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.header("Dados Detalhados por Filme")
    
    # Tabela interativa
    st.dataframe(
        filtered_df.sort_values('ROI', ascending=False)[
            ['Original_Title', 'Company', 'Release', 'Budget', 'Gross_Worldwide', 'ROI', 'Tipo_Filme']
        ],
        column_config={
            "Budget": st.column_config.NumberColumn(format="$%.0f"),
            "Gross_Worldwide": st.column_config.NumberColumn(format="$%.0f"),
            "ROI": st.column_config.NumberColumn(format="%.2f")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Botão para download
    st.download_button(
        label="📥 Baixar Dados Filtrados",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='marvel_dc_roi_analysis.csv',
        mime='text/csv'
    )

# Footer
st.markdown("""
<div class="footer" style="padding: 1rem; text-align: center; margin-top: 2rem;">
    <p>Dashboard desenvolvido com Streamlit | Análise de ROI Marvel vs DC</p>
</div>
""", unsafe_allow_html=True)
