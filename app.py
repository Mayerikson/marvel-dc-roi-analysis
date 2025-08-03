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

# CSS customizado com fundo temático
st.markdown("""
<style>
    /* Fundo principal com tema super-herói */
    .main .block-container {
        background: linear-gradient(45deg, 
            rgba(226, 54, 54, 0.1) 25%, 
            transparent 25%, 
            transparent 50%, 
            rgba(0, 120, 240, 0.1) 50%, 
            rgba(0, 120, 240, 0.1) 75%, 
            transparent 75%, 
            transparent);
        background-size: 60px 60px;
    }
    
    /* Padrão de fundo sutil */
    .stApp {
        background: linear-gradient(135deg, 
            rgba(226, 54, 54, 0.05) 0%, 
            rgba(255, 255, 255, 0.95) 50%, 
            rgba(0, 120, 240, 0.05) 100%);
    }
    
    .main-header {
        background: linear-gradient(90deg, #E23636 0%, #0078F0 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        border: 3px solid #FFD700;
    }
    
    .marvel-card {
        background: linear-gradient(135deg, #E23636, #FF6B6B);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 5px 15px rgba(226, 54, 54, 0.4);
        border: 2px solid #FFD700;
    }
    
    .dc-card {
        background: linear-gradient(135deg, #0078F0, #4A90E2);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 5px 15px rgba(0, 120, 240, 0.4);
        border: 2px solid #FFD700;
    }
    
    .winner-card {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-weight: bold;
        color: #333;
        box-shadow: 0 8px 20px rgba(255, 215, 0, 0.5);
        border: 3px solid #FF6347;
    }
    
    .insight-card {
        background: linear-gradient(135deg, #98FB98, #90EE90);
        padding: 1.5rem;
        border-radius: 15px;
        color: #2F4F2F;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(152, 251, 152, 0.4);
        border-left: 5px solid #32CD32;
    }
    
    .outlier-card {
        background: linear-gradient(135deg, #FF6347, #FF4500);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 5px 15px rgba(255, 99, 71, 0.4);
    }
    
    .conclusion-card {
        background: linear-gradient(135deg, #9370DB, #8A2BE2);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 20px rgba(147, 112, 219, 0.5);
        border: 3px solid #FFD700;
    }
    
    .footer {
        background: linear-gradient(90deg, #E23636 0%, #0078F0 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-top: 2rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    
    .stMetric {
        background: rgba(255,255,255,0.95);
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #FFD700;
        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .winner-metric {
        animation: pulse 2s infinite;
    }
    
    /* Símbolos de super-herói no fundo */
    .hero-symbol {
        position: fixed;
        opacity: 0.05;
        font-size: 8rem;
        z-index: -1;
        color: #FFD700;
    }
    
    .marvel-symbol {
        top: 10%;
        right: 10%;
        transform: rotate(15deg);
    }
    
    .dc-symbol {
        bottom: 10%;
        left: 10%;
        transform: rotate(-15deg);
    }
</style>

<!-- Símbolos de fundo -->
<div class="hero-symbol marvel-symbol">⚡</div>
<div class="hero-symbol dc-symbol">🦇</div>

""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🎬 MARVEL vs DC: ROI ANALYSIS 🏆</h1>
    <h3>Respostas às perguntas de negócio com controle de outliers</h3>
    <p><em>"Dados precisos para decisões estratégicas - Explicado de forma simples!"</em></p>
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
    <div class="winner-card winner-metric">
        <h3>🏆 Vencedor</h3>
        <h2>{winner['Franquia']}</h2>
        <p>ROI Médio: {winner['ROI Médio']:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

# Insight para a pergunta 1
st.markdown("""
<div class="insight-card">
    <h3>🧠 O que isso significa? (Explicação Simples)</h3>
    <p><strong>Imagine que você tem uma lojinha de doces:</strong></p>
    <ul>
        <li>🍭 ROI é como descobrir qual doce te dá mais dinheiro de volta</li>
        <li>📊 O gráfico mostra que uma franquia consegue ganhar mais dinheiro com cada real investido</li>
        <li>🎯 É como se uma franquia fosse melhor em transformar $1 em $3, enquanto a outra transforma $1 em $2</li>
        <li>💡 Para os empresários: investir na franquia vencedora historicamente deu mais retorno!</li>
    </ul>
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

# Insight para a pergunta 2
st.markdown("""
<div class="insight-card">
    <h3>🧠 O que isso significa? (Explicação Simples)</h3>
    <p><strong>Imagine que você está comprando ingredientes para fazer bolos:</strong></p>
    <ul>
        <li>🎂 Às vezes, gastar mais ingredientes não significa que seu bolo vai vender melhor</li>
        <li>💰 Alguns filmes gastam MUITO dinheiro mas não ganham proporcionalmente mais</li>
        <li>🎯 As bolinhas maiores são filmes que ganharam muito dinheiro no total</li>
        <li>📈 O segredo é encontrar o ponto doce: gastar o suficiente para fazer um bom filme, mas não desperdiçar</li>
        <li>🏆 Os melhores filmes estão no topo do gráfico: gastaram menos e ganharam muito!</li>
    </ul>
</div>
""", unsafe_allow_html=True)

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

# Insight para a pergunta 3
st.markdown("""
<div class="insight-card">
    <h3>🧠 O que isso significa? (Explicação Simples)</h3>
    <p><strong>Imagine que você tem uma banda de música:</strong></p>
    <ul>
        <li>🎵 "Filmes de Origem" são como sua primeira música - tudo é novidade e pode ser uma grande surpresa!</li>
        <li>🎶 "Sequências" são como fazer uma segunda música parecida - as pessoas já sabem o que esperar</li>
        <li>⭐ O gráfico mostra se é melhor apostar em histórias novas ou continuar histórias que já funcionaram</li>
        <li>🎭 Às vezes o público ama novidades, às vezes prefere personagens que já conhece</li>
        <li>💡 Para os estúdios: isso ajuda a decidir se vale mais apostar em herói novo ou fazer "Parte 2"</li>
    </ul>
</div>
""", unsafe_allow_html=True)

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

# Insight para a pergunta 4
st.markdown("""
<div class="insight-card">
    <h3>🧠 O que isso significa? (Explicação Simples)</h3>
    <p><strong>Imagine que você está observando duas equipes de futebol ao longo dos anos:</strong></p>
    <ul>
        <li>⚽ Cada linha mostra como cada "time" (Marvel vs DC) jogou ao longo do tempo</li>
        <li>📈 Quando a linha sobe, significa que o time teve um ano muito bom em ganhar dinheiro</li>
        <li>📉 Quando desce, foi um ano mais difícil</li>
        <li>🏃‍♂️ Você pode ver qual time está "na frente" em cada ano</li>
        <li>🎯 Para investidores: mostra as tendências - qual franquia está melhorando ou piorando com o tempo</li>
    </ul>
</div>
""", unsafe_allow_html=True)

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

# Insight para a pergunta 5
st.markdown("""
<div class="insight-card">
    <h3>🧠 O que isso significa? (Explicação Simples)</h3>
    <p><strong>Imagine um ranking dos melhores "negócios" do cinema:</strong></p>
    <ul>
        <li>🏆 Estes são os filmes que foram os "negócios da China" - gastaram pouco e ganharam MUITO!</li>
        <li>💎 São como encontrar um diamante barato que vale uma fortuna</li>
        <li>🎯 Para os estúdios: estes filmes são o modelo ideal de como fazer cinema que dá lucro</li>
        <li>🔍 Analisando estes campeões, dá para descobrir a "fórmula do sucesso"</li>
        <li>📚 É como estudar os melhores alunos da sala para saber como tirar nota 10!</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Análise de conclusão baseada nos dados
def get_winner_analysis(include_outliers):
    if include_outliers:
        analysis_df = df[df['Company'].isin(selected_companies)]
    else:
        analysis_df = df[(df['Company'].isin(selected_companies)) & (df['Outlier'] == 'Normal')]
    
    roi_by_company = analysis_df.groupby('Company')['ROI'].mean()
    winner = roi_by_company.idxmax()
    winner_roi = roi_by_company.max()
    loser = roi_by_company.idxmin()
    loser_roi = roi_by_company.min()
    
    return winner, winner_roi, loser, loser_roi

# Conclusão final
st.markdown("---")
st.header("🎯 Conclusões Estratégicas")

# Análise com e sem outliers
winner_with, roi_with, loser_with, roi_loser_with = get_winner_analysis(True)
winner_without, roi_without, loser_without, roi_loser_without = get_winner_analysis(False)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="marvel-card">
        <h3>📊 COM Outliers</h3>
        <h2>🏆 Vencedor: {winner_with}</h2>
        <p><strong>ROI Médio:</strong> {roi_with:.2f}</p>
        <p><strong>Perdedor:</strong> {loser_with} (ROI: {roi_loser_with:.2f})</p>
        <hr>
        <p><em>Inclui casos extremos como "Joker" que podem distorcer a análise</em></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="dc-card">
        <h3>📊 SEM Outliers</h3>
        <h2>🏆 Vencedor: {winner_without}</h2>
        <p><strong>ROI Médio:</strong> {roi_without:.2f}</p>
        <p><strong>Perdedor:</strong> {loser_without} (ROI: {roi_loser_without:.2f})</p>
        <hr>
        <p><em>Análise mais representativa para planejamento estratégico</em></p>
    </div>
    """, unsafe_allow_html=True)

# Explicação do ROI antes das conclusões
st.markdown("""
<div style="background: linear-gradient(135deg, #F0F8FF, #E6F3FF); padding: 2rem; border-radius: 15px; border-left: 5px solid #4169E1; margin: 2rem 0;">
    <h2>🤔 Mas afinal, o que é ROI?</h2>
    <p><strong>ROI significa "Return on Investment" (Retorno sobre Investimento)</strong></p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: #FFFFFF; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border: 2px solid #4169E1;">
    <h3>📊 Fórmula Simples:</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="font-size: 1.3em; background: #FFD700; padding: 1.5rem; border-radius: 10px; text-align: center; color: #333; font-weight: bold; margin: 1rem 0;">
    ROI = (Dinheiro Ganho - Dinheiro Investido) ÷ Dinheiro Investido
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: #F8F9FA; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border-left: 5px solid #28A745;">
    <h3>🎬 Exemplo Prático no Cinema:</h3>
    <p>💰 <strong>Investimento:</strong> Estúdio gasta $100 milhões para fazer um filme</p>
    <p>🎟️ <strong>Retorno:</strong> Filme arrecada $300 milhões no mundo todo</p>
    <p>📈 <strong>ROI:</strong> (300 - 100) ÷ 100 = 2.0 (ou 200%)</p>
    <p>✨ <strong>Significado:</strong> Para cada $1 investido, o estúdio ganhou $2 de lucro!</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: #FFD700; color: #333; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; text-align: center; font-size: 1.1em;">
    <strong>🎯 Por que ROI é importante?</strong><br>
    Mostra qual franquia é mais eficiente em transformar dinheiro investido em lucro!
</div>
""", unsafe_allow_html=True)

# Conclusão geral com cores específicas
if winner_with == winner_without:
    # Resultado consistente - usar cor da franquia vencedora
    if winner_with == "Marvel":
        conclusion_bg = "linear-gradient(135deg, #E23636, #FF6B6B, #FFB6C1)"
        text_color = "white"
        winner_symbol = "⚡"
        winner_theme = "Marvel - Cores vibrantes como o céu em ação dos filmes!"
    else:
        conclusion_bg = "linear-gradient(135deg, #0078F0, #4A90E2, #191970)"
        text_color = "white"
        winner_symbol = "🦇"
        winner_theme = "DC - Cores escuras e intensas como Gotham City!"
    
    conclusion_text = f"""
    <div style="background: {conclusion_bg}; padding: 2.5rem; border-radius: 20px; color: {text_color}; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.4); border: 4px solid #FFD700;">
        <h1 style="font-size: 3em;">{winner_symbol}</h1>
        <h2>🎉 RESULTADO CONSISTENTE!</h2>
        <h3 style="font-size: 2em; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">{winner_with} DOMINA EM AMBOS OS CENÁRIOS! {winner_symbol}</h3>
        <p style="font-size: 1.3em; margin: 1.5rem 0;">
            <strong>{winner_theme}</strong>
        </p>
        <p style="font-size: 1.1em;">
            Isso significa que <strong>{winner_with}</strong> tem uma vantagem consistente e confiável no ROI, 
            independentemente de incluirmos ou não casos extremos na análise.
        </p>
    </div>
    """
    
    # Adicionar recomendação separadamente
    recommendation_text = f"""
    <div style="background: rgba(255,255,255,0.95); padding: 2rem; border-radius: 15px; margin: 2rem 0; border: 3px solid #FFD700; color: #333;">
        <h3 style="color: #333;">💡 Recomendação Final para Investidores:</h3>
        <p style="font-size: 1.2em; color: #333;">
            Com base na análise de ROI histórico, investimentos em <strong>{winner_with}</strong> 
            demonstraram maior retorno consistente sobre o investimento.
        </p>
        <div style="background: #28A745; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            <p style="margin: 0;"><strong>🎯 Confiabilidade:</strong> Vence tanto com quanto sem outliers!</p>
        </div>
        <div style="background: #17A2B8; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            <p style="margin: 0;"><strong>📈 Estratégia:</strong> Franquia mais segura para investimentos futuros!</p>
        </div>
    </div>
    """
else:
    # Resultados diferentes - mostrar ambas as franquias
    conclusion_text = f"""
    <div style="background: linear-gradient(45deg, #E23636, #0078F0); padding: 2.5rem; border-radius: 20px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.4); border: 4px solid #FFD700;">
        <h1 style="font-size: 3em;">⚔️</h1>
        <h2>⚠️ BATALHA ÉPICA - RESULTADOS DIFERENTES!</h2>
        
        <div style="display: flex; justify-content: space-around; margin: 2rem 0;">
            <div style="background: linear-gradient(135deg, #E23636, #FF6B6B); padding: 1.5rem; border-radius: 15px; flex: 1; margin: 0 1rem;">
                <h3>⚡ COM OUTLIERS</h3>
                <h2>{winner_with} VENCE!</h2>
                <p>Cores vibrantes como tempestades!</p>
            </div>
            
            <div style="background: linear-gradient(135deg, #0078F0, #191970); padding: 1.5rem; border-radius: 15px; flex: 1; margin: 0 1rem;">
                <h3>🦇 SEM OUTLIERS</h3>
                <h2>{winner_without} VENCE!</h2>
                <p>Cores escuras como a noite!</p>
            </div>
        </div>
        
        <p style="font-size: 1.1em;">
            Isso significa que casos extremos estão influenciando significativamente os resultados!
        </p>
        
        <div style="background: rgba(255,255,255,0.2); padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
            <h3>💡 Recomendação Estratégica:</h3>
            <p style="font-size: 1.2em;">
                Para decisões de investimento, foque na análise <strong>SEM outliers</strong>:<br>
                <span style="background: {'linear-gradient(135deg, #E23636, #FF6B6B)' if winner_without == 'Marvel' else 'linear-gradient(135deg, #0078F0, #191970)'}; padding: 0.5rem 1rem; border-radius: 10px; font-size: 1.3em;">
                    🏆 {winner_without} é a escolha mais segura!
                </span>
                <br><br>
                🎯 Representa o desempenho típico, sem casos extremos<br>
                📊 Mais confiável para previsões futuras
            </p>
        </div>
    </div>
    """

st.markdown(conclusion_text, unsafe_allow_html=True)

# Renderizar recomendação separadamente para resultado consistente
if winner_with == winner_without:
    st.markdown(recommendation_text, unsafe_allow_html=True)

if not include_outliers:
    st.success("""
    **✅ Análise sem outliers (recomendada para estratégia):**
    - Fornece uma visão mais representativa do desempenho típico das franquias
    - Útil para planejamento estratégico e previsões confiáveis
    - Remove casos extremos que podem criar expectativas irreais
    """)
else:
    st.warning("""
    **⚠️ Análise incluindo outliers:**
    - Mostra casos excepcionais que podem distorcer as médias
    - Útil para identificar oportunidades excepcionais ou riscos extremos
    - Pode criar expectativas irreais baseadas em sucessos atípicos
    """)

st.markdown("""
<div class="footer">
    <p>📊 Análise Completa de ROI Marvel vs DC | Insights para Todos! 🎬</p>
    <p>💡 Dashboard Interativo 2025 | Explicações Simples + Análise Profissional 🏆</p>
    <p>🦸‍♂️ Desenvolvido com Streamlit | Marvel ⚡ vs DC 🦇</p>
</div>
""", unsafe_allow_html=True)
