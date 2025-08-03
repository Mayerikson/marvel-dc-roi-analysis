import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
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
    .marvel-card {
        background: linear-gradient(135deg, #E23636, #FF6B6B);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .dc-card {
        background: linear-gradient(135deg, #0078F0, #4A90E2);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .winner-card {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 1rem;
        border-radius: 10px;
        color: #333;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .outlier-card {
        background: linear-gradient(135deg, #FF6347, #FF4500);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .footer {
        background: linear-gradient(90deg, #E23636 0%, #0078F0 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-top: 3rem;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.9);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .winner-metric {
        animation: pulse 2s infinite;
    }
    /* Customizar sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f0f2f6 0%, #e8eaf0 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🎬 MARVEL vs DC: ROI ANALYSIS 🏆</h1>
    <h3>Análise de Retorno sobre Investimento com Tratamento de Outliers</h3>
    <p><em>"Dados não mentem - descubra qual franquia entrega melhor ROI!"</em></p>
</div>
""", unsafe_allow_html=True)

# Função para detectar outliers usando IQR
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

# Carregar e preparar dados
@st.cache_data
def load_data():
    # Carregue seu arquivo CSV aqui
    # data = pd.read_csv('db.csv')
    
    # Dados de exemplo (substitua pelo seu CSV real)
    data = {
        'Original_Title': [
            'Joker', 'Venom', 'Aquaman', 'Wonder Woman', 'Batman v Superman',
            'Iron Man', 'The Avengers', 'Guardians of the Galaxy', 'Iron Man 2', 'Thor',
            'Black Panther', 'Avengers: Endgame', 'Captain Marvel', 'Spider-Man', 'Deadpool',
            'Justice League', 'Man of Steel', 'The Dark Knight', 'Suicide Squad', 'Shazam!'
        ],
        'Company': [
            'DC', 'Marvel', 'DC', 'DC', 'DC',
            'Marvel', 'Marvel', 'Marvel', 'Marvel', 'Marvel',
            'Marvel', 'Marvel', 'Marvel', 'Marvel', 'Marvel',
            'DC', 'DC', 'DC', 'DC', 'DC'
        ],
        'Release': [
            2019, 2018, 2018, 2017, 2016,
            2008, 2012, 2014, 2010, 2011,
            2018, 2019, 2019, 2017, 2016,
            2017, 2013, 2008, 2016, 2019
        ],
        'Budget': [
            55000000, 100000000, 160000000, 149000000, 250000000,
            140000000, 220000000, 170000000, 200000000, 150000000,
            200000000, 356000000, 152000000, 175000000, 58000000,
            300000000, 225000000, 185000000, 175000000, 100000000
        ],
        'Gross_Worldwide': [
            1074251311, 856085151, 1148161807, 821847012, 873634919,
            585366247, 1518812988, 773328629, 623933331, 449326618,
            1346913161, 2797800564, 1128274794, 880166877, 783112979,
            657924295, 668045518, 1004558444, 746846894, 366021897
        ]
    }
    df = pd.DataFrame(data)
    
    # Calcular ROI
    df['ROI'] = (df['Gross_Worldwide'] - df['Budget']) / df['Budget']
    
    # Detectar outliers
    df = detect_outliers(df)
    
    # Classificar tipo de filme
    sequel_keywords = ['2', '3', 'II', 'III', 'Age of', 'Civil War', 'Endgame', 'Infinity', 'v Superman']
    df['Tipo_Filme'] = df['Original_Title'].apply(
        lambda x: 'Sequência/Continuação' if any(keyword in str(x) for keyword in sequel_keywords) 
        else 'Filme de Origem'
    )
    
    # Classificar faixa de orçamento
    df['Faixa_Orcamento'] = pd.cut(
        df['Budget'],
        bins=[0, 100000000, 200000000, float('inf')],
        labels=['Baixo (< $100M)', 'Médio ($100M-200M)', 'Alto (> $200M)']
    )
    
    return df

df = load_data()

# Sidebar com filtros
st.sidebar.header('⚙️ Configurações de Análise')

# Opção para incluir/excluir outliers
include_outliers = st.sidebar.checkbox(
    'Incluir outliers (ex: Joker)',
    value=False,
    help="Outliers podem distorcer a análise. Recomendado desmarcar para análise principal."
)

# Filtros interativos
selected_companies = st.sidebar.multiselect(
    'Selecione as Franquias',
    options=df['Company'].unique(),
    default=df['Company'].unique()
)

year_range = st.sidebar.slider(
    'Intervalo de Anos',
    min_value=int(df['Release'].min()),
    max_value=int(df['Release'].max()),
    value=(int(df['Release'].min()), int(df['Release'].max()))
)

movie_types = st.sidebar.multiselect(
    'Tipo de Filme',
    options=df['Tipo_Filme'].unique(),
    default=df['Tipo_Filme'].unique()
)

budget_ranges = st.sidebar.multiselect(
    'Faixa de Orçamento',
    options=df['Faixa_Orcamento'].unique(),
    default=df['Faixa_Orcamento'].unique()
)

# Aplicar filtros
filtered_df = df[
    (df['Company'].isin(selected_companies)) &
    (df['Release'].between(year_range[0], year_range[1])) &
    (df['Tipo_Filme'].isin(movie_types)) &
    (df['Faixa_Orcamento'].isin(budget_ranges))
]

if not include_outliers:
    filtered_df = filtered_df[filtered_df['Outlier'] == 'Normal']

# Mostrar aviso sobre outliers excluídos
if not include_outliers and any(df['Outlier'] == 'Outlier'):
    outliers = df[df['Outlier'] == 'Outlier']
    with st.expander("⚠️ Outliers Excluídos da Análise"):
        st.markdown("""
        <div class="outlier-card">
            <h3>Os seguintes filmes foram identificados como outliers:</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for _, row in outliers.iterrows():
            st.markdown(f"""
            <div style="background: rgba(255,99,71,0.2); padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0;">
                <strong>{row['Original_Title']}</strong> (ROI: {row['ROI']:.2f})
                <br>Orçamento: ${row['Budget']/1e6:.1f}M | Receita: ${row['Gross_Worldwide']/1e6:.1f}M
            </div>
            """, unsafe_allow_html=True)
        
        st.info("""
        Estes filmes foram automaticamente identificados como valores extremos que podem distorcer a análise. 
        Você pode incluí-los marcando a opção "Incluir outliers" na sidebar.
        """)

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
    min_budget_high_roi = filtered_df[filtered_df['ROI'] > filtered_df['ROI'].median()]['Budget'].min()
    st.metric("Menor Orçamento com ROI Acima da Mediana", f"${min_budget_high_roi/1e6:.1f}M")

# Análises em abas
tab1, tab2, tab3 = st.tabs(["📈 Análise Comparativa", "💰 Relação Orçamento-ROI", "🎬 Detalhes por Filme"])

with tab1:
    st.header("Comparativo entre Franquias")
    
    # ROI por empresa
    fig1 = px.box(
        filtered_df,
        x='Company',
        y='ROI',
        color='Company',
        color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
        points="all",
        hover_data=['Original_Title', 'Release', 'Budget'],
        title="Distribuição de ROI por Franquia"
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Evolução temporal
    st.subheader("Evolução do ROI ao Longo dos Anos")
    fig2 = px.line(
        filtered_df.groupby(['Release', 'Company'])['ROI'].mean().reset_index(),
        x='Release',
        y='ROI',
        color='Company',
        color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
        markers=True,
        title="Tendência Anual do ROI"
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("Relação entre Orçamento e ROI")
    
    # Gráfico de bolhas
    fig3 = px.scatter(
        filtered_df,
        x='Budget',
        y='ROI',
        color='Company',
        size='Gross_Worldwide',
        hover_name='Original_Title',
        log_x=True,
        color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
        title="Orçamento vs ROI (Tamanho pela Receita Mundial)"
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # ROI por faixa de orçamento
    st.subheader("ROI Médio por Faixa de Orçamento")
    fig4 = px.bar(
        filtered_df.groupby(['Company', 'Faixa_Orcamento'])['ROI'].mean().reset_index(),
        x='Faixa_Orcamento',
        y='ROI',
        color='Company',
        barmode='group',
        color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
        title="Performance por Nível de Investimento"
    )
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.header("Detalhes por Filme")
    
    # Tabela interativa
    st.dataframe(
        filtered_df.sort_values('ROI', ascending=False)[
            ['Original_Title', 'Company', 'Release', 'Budget', 'Gross_Worldwide', 'ROI', 'Tipo_Filme']
        ],
        column_config={
            "Budget": st.column_config.NumberColumn("Orçamento", format="$%.0f"),
            "Gross_Worldwide": st.column_config.NumberColumn("Receita Mundial", format="$%.0f"),
            "ROI": st.column_config.NumberColumn("ROI", format="%.2f"),
            "Release": st.column_config.NumberColumn("Ano", format="%d")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Botão para download
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados Filtrados (CSV)",
        data=csv,
        file_name='marvel_dc_roi_analysis.csv',
        mime='text/csv'
    )

# Footer
st.markdown("""
<div class="footer">
    <h3>🎬 MARVEL vs DC: ROI ANALYSIS</h3>
    <p>Dashboard desenvolvido com Streamlit | Análise de dados financeiros de filmes</p>
    <p><em>"O verdadeiro vencedor é aquele que entrega o melhor retorno!"</em></p>
</div>
""", unsafe_allow_html=True)
