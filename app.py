import streamlit as st
import pandas as pd
import plotly.express as px
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
            ["Captain Marvel","Marvel",6.9,64,123,2019,175000000,153433423,426829839,1128274794],
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
    df['Is_Sequel'] = df['Original_Title'].apply(lambda x: int(any(kw in str(x) for kw in sequel_keywords))
    
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
st.markdown(f"""
**📝 Notas Metodológicas:**
- ROI calculado como: (Bilheteria Mundial - Orçamento) / Orçamento
- Dados coletados de fontes públicas (IMDB, Box Office Mojo)
- Análise considera {len(df)} filmes (Marvel: {marvel_count}, DC: {dc_count})
""")
