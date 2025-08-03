mport streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import random

# Configuração da página
st.set_page_config(
    page_title="🦸‍♂️ Marvel vs DC: Análise de ROI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado com tema super-herói mais elaborado
st.markdown("""
<style>
    @import url(\'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@300;400;500;700&display=swap\');
    
    /* Variáveis CSS para cores Marvel/DC */
    :root {
        --marvel-red: #ED1D24;
        --marvel-blue: #518CCA;
        --marvel-yellow: #F78F1E;
        --dc-blue: #0078F0;
        --dc-red: #DC143C;
        --dc-gold: #FFD700;
        --hero-dark: #1E1E1E;
        --hero-light: #F5F5F5;
        --accent-green: #00FF41;
        --accent-purple: #8A2BE2;
    }
    
    /* Fundo principal com padrão de quadrinhos */
    .stApp {
        background: linear-gradient(135deg, 
            rgba(237, 29, 36, 0.03) 0%, 
            rgba(255, 255, 255, 0.97) 25%,
            rgba(0, 120, 240, 0.03) 50%,
            rgba(255, 255, 255, 0.97) 75%,
            rgba(237, 29, 36, 0.03) 100%);
        background-attachment: fixed;
    }
    
    /* Padrão de pontos tipo quadrinhos */
    .main .block-container::before {
        content: \'\';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 25% 25%, rgba(237, 29, 36, 0.1) 2px, transparent 2px),
            radial-gradient(circle at 75% 75%, rgba(0, 120, 240, 0.1) 2px, transparent 2px);
        background-size: 50px 50px;
        z-index: -1;
        pointer-events: none;
    }
    
    /* Header principal estilo quadrinhos */
    .main-header {
        background: linear-gradient(45deg, 
            var(--marvel-red) 0%, 
            var(--marvel-yellow) 25%,
            var(--dc-blue) 75%, 
            var(--dc-gold) 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 
            0 10px 30px rgba(0,0,0,0.3),
            inset 0 1px 0 rgba(255,255,255,0.2);
        border: 4px solid var(--dc-gold);
        position: relative;
        overflow: hidden;
        font-family: \'Orbitron\', monospace;
    }
    
    .main-header::before {
        content: \'\';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(255,255,255,0.1) 10px,
            rgba(255,255,255,0.1) 20px
        );
        animation: heroShine 3s linear infinite;
    }
    
    @keyframes heroShine {
        0% { transform: translateX(-100%) translateY(-100%); }
        100% { transform: translateX(100%) translateY(100%); }
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 900;
        text-shadow: 3px 3px 0px rgba(0,0,0,0.5);
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .main-header h3 {
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-style: italic;
        font-size: 1rem;
        position: relative;
        z-index: 1;
    }
    
    /* Cards temáticos melhorados */
    .marvel-card {
        background: linear-gradient(135deg, 
            var(--marvel-red) 0%, 
            #FF4757 50%,
            var(--marvel-yellow) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 
            0 8px 25px rgba(237, 29, 36, 0.4),
            inset 0 1px 0 rgba(255,255,255,0.2);
        border: 3px solid var(--dc-gold);
        position: relative;
        overflow: hidden;
        font-family: \'Roboto\', sans-serif;
    }
    
    .marvel-card::before {
        content: \'⚡\';
        position: absolute;
        top: 10px;
        right: 10px;
        font-size: 2rem;
        opacity: 0.3;
        animation: float 2s ease-in-out infinite;
    }
    
    .dc-card {
        background: linear-gradient(135deg, 
            var(--dc-blue) 0%, 
            #4A90E2 50%,
            #2C5282 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 
            0 8px 25px rgba(0, 120, 240, 0.4),
            inset 0 1px 0 rgba(255,255,255,0.2);
        border: 3px solid var(--dc-gold);
        position: relative;
        overflow: hidden;
        font-family: \'Roboto\', sans-serif;
    }
    
    .dc-card::before {
        content: \'🦇\';
        position: absolute;
        top: 10px;
        right: 10px;
        font-size: 2rem;
        opacity: 0.3;
        animation: float 2s ease-in-out infinite reverse;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Card vencedor com animação */
    .winner-card {
        background: linear-gradient(135deg, 
            var(--dc-gold) 0%, 
            #FFA500 50%,
            #FF8C00 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        color: var(--hero-dark);
        box-shadow: 
            0 12px 35px rgba(255, 215, 0, 0.6),
            inset 0 1px 0 rgba(255,255,255,0.3);
        border: 4px solid var(--marvel-red);
        position: relative;
        overflow: hidden;
        font-family: \'Orbitron\', monospace;
    }
    
    .winner-card::before {
        content: \'🏆\';
        position: absolute;
        top: -20px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 3rem;
        animation: bounce 1s ease-in-out infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateX(-50%) translateY(0px); }
        50% { transform: translateX(-50%) translateY(-10px); }
    }
    
    /* Cards de insight mais amigáveis */
    .insight-card {
        background: linear-gradient(135deg, 
            #E8F5E8 0%, 
            #F0FFF0 50%,
            #E8F5E8 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: #2F4F2F;
        margin: 1rem 0;
        box-shadow: 
            0 5px 20px rgba(152, 251, 152, 0.3),
            inset 0 1px 0 rgba(255,255,255,0.5);
        border-left: 6px solid var(--accent-green);
        position: relative;
        font-family: \'Roboto\', sans-serif;
    }
    
    .insight-card::before {
        content: \'💡\';
        position: absolute;
        top: 15px;
        right: 15px;
        font-size: 1.5rem;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.7; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.1); }
    }
    
    .insight-card h3 {
        color: #228B22;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .insight-card ul {
        margin: 0;
        padding-left: 1.5rem;
    }
    
    .insight-card li {
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }
    
    /* Card de outliers */
    .outlier-card {
        background: linear-gradient(135deg, 
            #FF6B6B 0%, 
            #FF5252 50%,
            #F44336 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 
            0 8px 25px rgba(255, 107, 107, 0.4),
            inset 0 1px 0 rgba(255,255,255,0.2);
        border: 3px solid var(--dc-gold);
        position: relative;
        font-family: \'Roboto\', sans-serif;
    }
    
    .outlier-card::before {
        content: \'⚠️\';
        position: absolute;
        top: 10px;
        right: 10px;
        font-size: 1.5rem;
        animation: shake 0.5s ease-in-out infinite;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-2px); }
        75% { transform: translateX(2px); }
    }
    
    /* Card de conclusão épico */
    .conclusion-card {
        background: linear-gradient(135deg, 
            var(--accent-purple) 0%, 
            #9932CC 50%,
            #8B008B 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 
            0 15px 40px rgba(147, 112, 219, 0.5),
            inset 0 1px 0 rgba(255,255,255,0.2);
        border: 4px solid var(--dc-gold);
        position: relative;
        overflow: hidden;
        font-family: \'Orbitron\', monospace;
    }
    
    .conclusion-card::before {
        content: \'\';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255,255,255,0.2), 
            transparent);
        animation: sweep 3s ease-in-out infinite;
    }
    
    @keyframes sweep {
        0% { left: -100%; }
        50% { left: 100%; }
        100% { left: 100%; }
    }
    
    /* Footer heroico */
    .footer {
        background: linear-gradient(90deg, 
            var(--marvel-red) 0%, 
            var(--marvel-yellow) 25%,
            var(--dc-blue) 75%, 
            var(--dc-gold) 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-top: 2rem;
        box-shadow: 
            0 10px 30px rgba(0,0,0,0.3),
            inset 0 1px 0 rgba(255,255,255,0.2);
        border: 4px solid var(--hero-dark);
        font-family: \'Orbitron\', monospace;
        position: relative;
    }
    
    /* Métricas estilizadas */
    .stMetric {
        background: linear-gradient(135deg, 
            rgba(255,255,255,0.95) 0%, 
            rgba(248,249,250,0.95) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 6px solid var(--dc-gold);
        box-shadow: 
            0 5px 15px rgba(0,0,0,0.1),
            inset 0 1px 0 rgba(255,255,255,0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 
            0 10px 25px rgba(0,0,0,0.2),
            inset 0 1px 0 rgba(255,255,255,0.5);
    }
    
    /* Animação para métricas vencedoras */
    .winner-metric {
        animation: heroGlow 2s ease-in-out infinite;
        border-left-color: var(--dc-gold);
    }
    
    @keyframes heroGlow {
        0%, 100% { 
            box-shadow: 
                0 5px 15px rgba(0,0,0,0.1),
                0 0 20px rgba(255, 215, 0, 0.3);
        }
        50% { 
            box-shadow: 
                0 8px 25px rgba(0,0,0,0.2),
                0 0 30px rgba(255, 215, 0, 0.6);
        }
    }
    
    /* Símbolos de super-herói flutuantes */
    .hero-symbol {
        position: fixed;
        opacity: 0.08;
        font-size: 6rem;
        z-index: -1;
        color: var(--dc-gold);
        animation: floatSlow 6s ease-in-out infinite;
        pointer-events: none;
    }
    
    .marvel-symbol {
        top: 15%;
        right: 8%;
        animation-delay: 0s;
    }
    
    .dc-symbol {
        bottom: 15%;
        left: 8%;
        animation-delay: 3s;
    }
    
    .extra-symbol-1 {
        top: 60%;
        right: 20%;
        font-size: 4rem;
        animation-delay: 1.5s;
    }
    
    .extra-symbol-2 {
        top: 30%;
        left: 15%;
        font-size: 5rem;
        animation-delay: 4.5s;
    }
    
    @keyframes floatSlow {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        33% { transform: translateY(-20px) rotate(5deg); }
        66% { transform: translateY(10px) rotate(-3deg); }
    }
    
    /* Sidebar customizada */
    .css-1d391kg {
        background: linear-gradient(180deg, 
            rgba(237, 29, 36, 0.05) 0%, 
            rgba(255, 255, 255, 0.95) 50%,
            rgba(0, 120, 240, 0.05) 100%);
    }
    
    /* Botões e controles */
    .stButton > button {
        background: linear-gradient(135deg, 
            var(--marvel-red) 0%, 
            var(--dc-blue) 100%);
        color: white;
        border: 2px solid var(--dc-gold);
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
        font-family: \'Roboto\', sans-serif;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Checkbox e selectbox */
    .stCheckbox > label {
        font-family: \'Roboto\', sans-serif;
        font-weight: 500;
    }
    
    .stSelectbox > label {
        font-family: \'Roboto\', sans-serif;
        font-weight: 500;
        color: var(--hero-dark);
    }
    
    /* Headers personalizados */
    h1, h2, h3 {
        font-family: \'Orbitron\', monospace;
        color: var(--hero-dark);
    }
    
    /* Dataframe customizado */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        
        .hero-symbol {
            font-size: 4rem;
        }
        
        .winner-card, .conclusion-card {
            padding: 1.5rem;
        }
    }
</style>

<!-- Símbolos de fundo animados -->
<div class=\"hero-symbol marvel-symbol\">⚡</div>
<div class=\"hero-symbol dc-symbol\">🦇</div>
<div class=\"hero-symbol extra-symbol-1\">🛡️</div>
<div class=\"hero-symbol extra-symbol-2\">⭐</div>

\"\"\", unsafe_allow_html=True)

# Header principal épico
st.markdown(\"\"\"
<div class=\"main-header\">
    <h1>🦸‍♂️ MARVEL vs DC: BATALHA DOS DADOS 🦸‍♀️</h1>
    <h3>Análise Estratégica de ROI com Insights Humanos</h3>
    <p><em>\"Quando os números contam histórias épicas - Desvendando os segredos do sucesso cinematográfico!\"</em></p>
</div>
\"\"\", unsafe_allow_html=True)

# Função para detectar outliers usando IQR
def detect_outliers(df, column=\'ROI\'):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    df[\'Outlier\'] = df[column].apply(
        lambda x: \'Outlier\' if (x < lower_bound) or (x > upper_bound) else \'Normal\'
    )
    return df

# Carregar e preparar dados
@st.cache_data
def load_data():
    \"\"\"
    Carrega o dataset do Kaggle Marvel vs DC
    
    IMPORTANTE: Para usar seus dados reais, descomente a linha abaixo e 
    coloque o arquivo db.csv na mesma pasta do script:
    
    df = pd.read_csv(\'db.csv\')
    
    O dataset original tem as seguintes colunas:
    - Original Title: Nome do filme
    - Company: Marvel ou DC
    - Rate: Nota IMDB
    - Metascore: Pontuação Metacritic
    - Budget: Orçamento
    - Gross Worldwide: Receita mundial
    - Release: Ano de lançamento
    - Runtime: Duração
    - Genre: Gênero
    - Director: Diretor
    - Cast: Elenco principal
    \"\"\"
    
    # Para demonstração, usando dados simulados baseados no dataset real
    # SUBSTITUA por: df = pd.read_csv(\'db.csv\') quando tiver o arquivo
    
    data = {
        \'Original_Title\': [
            # Marvel (29 filmes)
            \'Iron Man\', \'The Incredible Hulk\', \'Iron Man 2\', \'Thor\', \'Captain America: The First Avenger\',
            \'The Avengers\', \'Iron Man Three\', \'Thor: The Dark World\', \'Captain America: The Winter Soldier\',
            \'Guardians of the Galaxy\', \'Avengers: Age of Ultron\', \'Ant-Man\', \'Captain America: Civil War\',
            \'Doctor Strange\', \'Guardians of the Galaxy Vol. 2\', \'Spider-Man: Homecoming\', \'Thor: Ragnarok\',
            \'Black Panther\', \'Avengers: Infinity War\', \'Ant-Man and the Wasp\', \'Captain Marvel\',
            \'Avengers: Endgame\', \'Spider-Man: Far From Home\', \'Deadpool\', \'Deadpool 2\',
            \'Logan\', \'X-Men: Days of Future Past\', \'X-Men: Apocalypse\', \'Venom\',
            # DC (12 filmes)
            \'Man of Steel\', \'Batman v Superman: Dawn of Justice\', \'Suicide Squad\', \'Wonder Wo
(Content truncated due to size limit. Use page ranges or line ranges to read remaining content)
