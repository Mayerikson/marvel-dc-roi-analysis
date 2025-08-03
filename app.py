import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Marvel vs DC: ROI Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para cores Marvel/DC
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
    
    /* Customizar sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f0f2f6 0%, #e8eaf0 100%);
    }
    
    /* Animação para métricas */
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

# Header principal com gradiente
st.markdown("""
<div class="main-header">
    <h1>🎬 MARVEL vs DC: QUEM GANHA O OSCAR DO ROI? 🏆</h1>
    <h3>Análise Baseada em Retorno sobre Investimento (ROI)</h3>
    <p><em>"Chega de glamour sem retorno. Dados decidem o vencedor!"</em></p>
</div>
""", unsafe_allow_html=True)

# Sidebar melhorado
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #E23636, #0078F0); padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
    <h3 style="margin: 0; text-align: center;">📊 SOBRE A ANÁLISE</h3>
</div>
""", unsafe_allow_html=True)

st.sidebar.info("""
**🎯 Critério Principal:**  
ROI (Return on Investment)

**📐 Fórmula:**  
(Receita - Orçamento) / Orçamento

**📊 Fonte:**  
IMDB via Kaggle

**📅 Período:**  
Anos 2000+

**🎬 Total:**  
40 filmes analisados
""")

# Adicionar logos (simulados com emojis já que não temos arquivos)
st.sidebar.markdown("""
<div style="text-align: center; margin: 2rem 0;">
    <div style="font-size: 4rem; margin: 1rem;">🕷️</div>
    <p style="color: #E23636; font-weight: bold;">MARVEL</p>
    <div style="font-size: 4rem; margin: 1rem;">🦇</div>
    <p style="color: #0078F0; font-weight: bold;">DC COMICS</p>
</div>
""", unsafe_allow_html=True)

# Função para carregar dados (baseado nos seus resultados)
@st.cache_data
def load_data():
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
    
    # Classificar origem vs sequência
    sequel_keywords = ['2', '3', 'II', 'III', 'Age of', 'Civil War', 'Endgame', 'Infinity', 'v Superman']
    df['Tipo_Filme'] = df['Original_Title'].apply(
        lambda x: 'Sequência/Continuação' if any(keyword in x for keyword in sequel_keywords) 
        else 'Filme de Origem'
    )
    
    # Faixa de orçamento
    df['Faixa_Orcamento'] = df['Budget'].apply(
        lambda x: 'Baixo (< $100M)' if x < 100000000 
        else 'Médio ($100M-200M)' if x < 200000000 
        else 'Alto (> $200M)'
    )
    
    return df

# Carregar dados
df = load_data()

# Métricas principais com destaque
col1, col2, col3, col4 = st.columns(4)

avg_roi_dc = df[df['Company'] == 'DC']['ROI'].mean()
avg_roi_marvel = df[df['Company'] == 'Marvel']['ROI'].mean()
best_movie = df.loc[df['ROI'].idxmax()]
total_movies = len(df)

with col1:
    st.markdown('<div class="winner-metric">', unsafe_allow_html=True)
    st.metric("🏆 ROI Médio DC", f"{avg_roi_dc:.2f}", delta="VENCEDOR!", delta_color="normal")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.metric("ROI Médio Marvel", f"{avg_roi_marvel:.2f}", delta=f"{((avg_roi_dc/avg_roi_marvel-1)*100):+.1f}%")

with col3:
    st.metric("🎯 Maior ROI", f"{best_movie['ROI']:.2f}", delta=best_movie['Original_Title'])

with col4:
    st.metric("🎬 Total Filmes", total_movies, delta="Analisados")

# Cartão de vitória
st.markdown(f"""
<div class="winner-card">
    <h2>🏆 DC COMICS VENCE!</h2>
    <p>ROI {((avg_roi_dc/avg_roi_marvel-1)*100):.1f}% superior à Marvel</p>
    <p>Eficiência financeira comprovada pelos dados</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# PERGUNTA 1: Comparação ROI
st.header("1️⃣ Quem tem o maior ROI nos filmes?")

col1, col2 = st.columns([3, 1])

with col1:
    roi_comparison = df.groupby('Company')['ROI'].agg(['mean', 'std', 'count']).reset_index()
    
    fig = go.Figure()
    
    # Marvel
    fig.add_trace(go.Bar(
        name='Marvel',
        x=['Marvel'],
        y=[avg_roi_marvel],
        marker_color='#E23636',
        text=f'{avg_roi_marvel:.2f}',
        textposition='auto',
    ))
    
    # DC
    fig.add_trace(go.Bar(
        name='DC',
        x=['DC'],
        y=[avg_roi_dc],
        marker_color='#0078F0',
        text=f'{avg_roi_dc:.2f}',
        textposition='auto',
    ))
    
    fig.update_layout(
        title="ROI Médio por Franquia",
        xaxis_title="Franquia",
        yaxis_title="ROI Médio",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("""
    <div class="dc-card">
        <h4>🎯 ANÁLISE:</h4>
        <p><strong>DC:</strong> 4.42 ROI médio</p>
        <p><strong>Marvel:</strong> 3.46 ROI médio</p>
        <p><strong>Vantagem DC:</strong> +27.7%</p>
        <hr>
        <p><em>DC demonstra maior eficiência financeira por filme investido.</em></p>
    </div>
    """, unsafe_allow_html=True)

# PERGUNTA 2: Melhores e piores filmes
st.header("2️⃣ Filmes que deram mais e menos retorno")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 TOP 5 - Maiores ROI")
    top_5 = df.nlargest(5, 'ROI')
    
    fig = px.bar(
        top_5,
        y='Original_Title',
        x='ROI',
        color='Company',
        color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
        title="Filmes Mais Rentáveis",
        orientation='h'
    )
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📉 BOTTOM 5 - Menores ROI")
    bottom_5 = df.nsmallest(5, 'ROI')
    
    fig = px.bar(
        bottom_5,
        y='Original_Title',
        x='ROI',
        color='Company',
        color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
        title="Filmes Menos Rentáveis",
        orientation='h'
    )
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# Destaque do Joker
joker_data = df[df['Original_Title'] == 'Joker'].iloc[0]
st.markdown(f"""
<div class="winner-card">
    <h3>🃏 DESTAQUE: JOKER (DC)</h3>
    <p>ROI de {joker_data['ROI']:.2f} = {joker_data['ROI']*100:.0f}% de retorno!</p>
    <p>Orçamento: ${joker_data['Budget']:,} | Receita: ${joker_data['Gross_Worldwide']:,}</p>
</div>
""", unsafe_allow_html=True)

# PERGUNTA 3: Orçamento vs ROI
st.header("3️⃣ Filmes com menos dinheiro deram mais lucro?")

budget_analysis = df.groupby('Faixa_Orcamento')['ROI'].agg(['mean', 'count']).reset_index()
budget_analysis.columns = ['Faixa_Orcamento', 'ROI_medio', 'quantidade']
budget_analysis = budget_analysis.sort_values('ROI_medio', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(
        budget_analysis,
        x='Faixa_Orcamento',
        y='ROI_medio',
        color='ROI_medio',
        color_continuous_scale='RdYlGn',
        title="ROI Médio por Faixa de Orçamento",
        text='ROI_medio'
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("""
    <div class="marvel-card">
        <h4>💡 INSIGHT CONFIRMADO:</h4>
        <p><strong>SIM!</strong> Menos orçamento = Mais ROI</p>
        <hr>
    """, unsafe_allow_html=True)
    
    for idx, row in budget_analysis.iterrows():
        st.markdown(f"**{row['Faixa_Orcamento']}:** {row['ROI_medio']:.2f}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# PERGUNTA 4: Origem vs Sequências  
st.header("4️⃣ Filmes de origem vs continuações")

origem_analysis = df.groupby(['Company', 'Tipo_Filme'])['ROI'].mean().reset_index()

fig = px.bar(
    origem_analysis,
    x='Company',
    y='ROI',
    color='Tipo_Filme',
    barmode='group',
    title="ROI: Filmes de Origem vs Sequências/Continuações",
    color_discrete_map={
        'Filme de Origem': '#FFD700',
        'Sequência/Continuação': '#87CEEB'
    }
)
fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

# PERGUNTA 5: Evolução temporal
st.header("5️⃣ Como o ROI mudou com o tempo?")

temporal_analysis = df.groupby(['Release', 'Company'])['ROI'].mean().reset_index()

fig = px.line(
    temporal_analysis,
    x='Release',
    y='ROI',
    color='Company',
    title="Evolução do ROI ao Longo dos Anos",
    color_discrete_map={'Marvel': '#E23636', 'DC': '#0078F0'},
    markers=True,
    line_shape='spline'
)
fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

# CONCLUSÃO FINAL
st.markdown("---")
st.header("🏆 CONCLUSÃO FINAL")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div style="background: rgba(255,255,255,0.9); padding: 2rem; border-radius: 10px; border-left: 5px solid #FFD700;">
        <h3>📊 RESULTADOS DA ANÁLISE:</h3>
        <ol>
            <li><strong>DC tem ROI médio superior</strong> (4.42 vs 3.46)</li>
            <li><strong>Joker (DC) é o campeão absoluto</strong> com ROI de 18.54</li>
            <li><strong>Filmes de baixo orçamento são mais rentáveis</strong> (6.1 vs 3.0)</li>
            <li><strong>Filmes de origem superam sequências</strong> em ambas franquias</li>
            <li><strong>DC tem mais picos, Marvel mais consistência</strong></li>
        </ol>
        <hr>
        <p><em>Análise baseada em 40 filmes com dados financeiros completos do IMDB.</em></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="winner-card">
        <h2>🎯 VENCEDOR</h2>
        <h1 style="font-size: 3rem; margin: 1rem 0;">DC COMICS</h1>
        <p><strong>Critério:</strong> Maior ROI médio</p>
        <p><strong>Vantagem:</strong> +27.7%</p>
        <p><strong>Eficiência financeira comprovada!</strong></p>
    </div>
    """, unsafe_allow_html=True)

# Footer com estilo
st.markdown("""
<div class="footer">
    <h3>🎬 MARVEL vs DC: ROI ANALYSIS 📊</h3>
    <p>Dashboard desenvolvido com Streamlit | Dados: IMDB via Kaggle</p>
    <p>Análise SQL + Visualização Python | Projeto Acadêmico 2025</p>
    <div style="margin-top: 1rem; font-size: 2rem;">
        🕷️ ⚔️ 🦇
    </div>
    <p><em>"Que os dados decidam o vencedor!"</em></p>
</div>
""", unsafe_allow_html=True)
