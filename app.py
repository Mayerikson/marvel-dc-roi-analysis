import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

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
    }
    .dc-card {
        background: linear-gradient(135deg, #0078F0, #4A90E2);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .winner-card {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .outlier-card {
        background: linear-gradient(135deg, #FF6347, #FF4500);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .footer {
        background: linear-gradient(90deg, #E23636 0%, #0078F0 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-top: 2rem;
    }
    .stMetric {
        background: rgba(255,255,255,0.9);
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
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🎬 MARVEL vs DC: ROI ANALYSIS 🏆</h1>
    <h3>Respostas às perguntas de negócio com controle de outliers</h3>
    <p><em>"Dados precisos para decisões estratégicas"</em></p>
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
    # df = pd.read_csv('db.csv')
    
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
        lambda x: 'Sequência' if any(keyword in str(x) for keyword in sequel_keywords) else 'Origem'
    )
    
    # Faixa de orçamento
    df['Faixa_Orcamento'] = pd.cut(
        df['Budget'],
        bins=[0, 100000000, 200000000, float('inf')],
        labels=['Baixo (<$100M)', 'Médio ($100M-$200M)', 'Alto (>$200M)']
    )
    
    return df

df = load_data()

# Sidebar com filtros
st.sidebar.header('⚙️ Controle de Análise')

# Opção para incluir/excluir outliers
include_outliers = st.sidebar.checkbox(
    'Incluir outliers (como Joker)',
    value=False,
    help="Outliers podem distorcer significativamente os resultados. Recomendado desativar para análise principal."
)

# Filtros adicionais
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

# Aplicar filtros
filtered_df = df[
    (df['Company'].isin(selected_companies)) &
    (df['Release'].between(year_range[0], year_range[1]))
]

if not include_outliers:
    filtered_df = filtered_df[filtered_df['Outlier'] == 'Normal']

# Mostrar aviso sobre outliers
if not include_outliers and any(df['Outlier'] == 'Outlier'):
    outliers = df[df['Outlier'] == 'Outlier']
    with st.expander("⚠️ Outliers Excluídos"):
        st.markdown("""
        <div class="outlier-card">
            <h3>Filmes identificados como outliers:</h3>
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
        Estes filmes têm valores de ROI extremamente altos ou baixos que podem distorcer a análise.
        Para incluí-los, marque a opção "Incluir outliers" na sidebar.
        """)

## Respostas às Perguntas de Negócio

# 1. Qual franquia tem melhor ROI médio?
st.header("1️⃣ Qual franquia tem melhor ROI médio?")

roi_comparison = filtered_df.groupby('Company')['ROI'].agg(['mean', 'count']).reset_index()
roi_comparison.columns = ['Franquia', 'ROI Médio', 'Número de Filmes']

col1, col2 = st.columns([3, 1])

with col1:
    fig = px.bar(
        roi_comparison,
        x='Franquia',
        y='ROI Médio',
        color='Franquia',
        color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
        text='ROI Médio',
        title="ROI Médio por Franquia"
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    winner = roi_comparison.loc[roi_comparison['ROI Médio'].idxmax()]
    st.markdown(f"""
    <div class="winner-card">
        <h3>🏆 Vencedor</h3>
        <h2>{winner['Franquia']}</h2>
        <p>ROI Médio: {winner['ROI Médio']:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

# 2. Como o ROI varia com o orçamento?
st.header("2️⃣ Como o ROI varia com o orçamento?")

fig = px.scatter(
    filtered_df,
    x='Budget',
    y='ROI',
    color='Company',
    size='Gross_Worldwide',
    hover_name='Original_Title',
    log_x=True,
    color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
    title="Relação entre Orçamento e ROI"
)
st.plotly_chart(fig, use_container_width=True)

# 3. Filmes de origem vs sequências
st.header("3️⃣ Filmes de origem têm melhor ROI que sequências?")

origin_vs_sequel = filtered_df.groupby(['Company', 'Tipo_Filme'])['ROI'].mean().reset_index()

fig = px.bar(
    origin_vs_sequel,
    x='Company',
    y='ROI',
    color='Tipo_Filme',
    barmode='group',
    color_discrete_map={'Origem': '#FFD700', 'Sequência': '#87CEEB'},
    title="ROI: Filmes de Origem vs Sequências"
)
st.plotly_chart(fig, use_container_width=True)

# 4. Evolução do ROI ao longo do tempo
st.header("4️⃣ Como o ROI evoluiu ao longo dos anos?")

fig = px.line(
    filtered_df.groupby(['Release', 'Company'])['ROI'].mean().reset_index(),
    x='Release',
    y='ROI',
    color='Company',
    color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
    markers=True,
    title="Evolução do ROI por Ano"
)
st.plotly_chart(fig, use_container_width=True)

# 5. Top 5 filmes por ROI
st.header("5️⃣ Quais são os filmes com maior ROI?")

top_movies = filtered_df.nlargest(5, 'ROI')[['Original_Title', 'Company', 'Release', 'ROI']]
top_movies['ROI'] = top_movies['ROI'].round(2)

st.dataframe(
    top_movies,
    column_config={
        "Original_Title": "Título",
        "Company": "Franquia",
        "Release": "Ano",
        "ROI": st.column_config.NumberColumn("ROI", format="%.2f")
    },
    hide_index=True,
    use_container_width=True
)

# Conclusão final
st.markdown("---")
st.header("🎯 Conclusões Estratégicas")

if not include_outliers:
    st.success("""
    **Análise sem outliers (recomendada):**
    - Fornece uma visão mais representativa do desempenho típico das franquias
    - Útil para planejamento estratégico e previsões
    """)
else:
    st.warning("""
    **Análise incluindo outliers:**
    - Mostra casos excepcionais que podem distorcer as médias
    - Útil para identificar oportunidades excepcionais ou riscos extremos
    """)

st.markdown("""
<div class="footer">
    <p>📊 Análise de ROI Marvel vs DC | Controle completo sobre outliers</p>
    <p>💡 Dados atualizados em 2025 | Dashboard desenvolvido com Streamlit</p>
</div>
""", unsafe_allow_html=True)
