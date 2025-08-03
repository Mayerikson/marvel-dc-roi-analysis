import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Marvel vs DC: ROI Analysis", page_icon="🦸", layout="wide")
st.title("🦸 Marvel vs DC: ROI Analysis")

# Leitura segura do CSV
try:
    df = pd.read_csv("db.csv", encoding="latin1")
except UnicodeDecodeError:
    df = pd.read_csv("db.csv", encoding="cp1252")

# Normalizar nomes das colunas
df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('�', '', regex=False)

# Mostrar nomes para conferência (remova depois de validar)
# st.write("Colunas disponíveis:", df.columns.tolist())

# Renomear se necessário (ajuste conforme seu CSV)
col_map = {
    'Original_Title': 'Original_Title',
    'Company': 'Company',
    'Budget': 'Budget',
    'Gross_Worldwide': 'Gross_Worldwide',
    'Release': 'Release',
}
# Detectar automaticamente nomes equivalentes
for expected_col in ['Original_Title', 'Company', 'Budget', 'Gross_Worldwide', 'Release']:
    matches = [col for col in df.columns if expected_col.lower() in col.lower()]
    if matches:
        col_map[expected_col] = matches[0]

df = df.rename(columns=col_map)

# Validar existência das colunas essenciais
required = ['Original_Title', 'Company', 'Budget', 'Gross_Worldwide', 'Release']
if not all(col in df.columns for col in required):
    st.error(f"Colunas obrigatórias ausentes. Verifique se existem: {required}")
    st.stop()

# Processamento de dados
df['Budget'] = pd.to_numeric(df['Budget'], errors='coerce')
df['Gross_Worldwide'] = pd.to_numeric(df['Gross_Worldwide'], errors='coerce')
df['ROI'] = (df['Gross_Worldwide'] - df['Budget']) / df['Budget']
df = df.dropna(subset=['ROI', 'Budget', 'Gross_Worldwide'])

df['Faixa_Orcamento'] = pd.cut(df['Budget'], 
    bins=[0, 100_000_000, 200_000_000, float('inf')],
    labels=['Baixo (< $100M)', 'Médio ($100M-$200M)', 'Alto (> $200M)']
)

sequels = ['2', '3', 'II', 'III', 'Four', 'Age of', 'Civil War', 'Endgame', 'Infinity']
df['Tipo_Filme'] = df['Original_Title'].apply(
    lambda x: 'Sequência/Continuação' if any(s in str(x) for s in sequels) else 'Filme de Origem'
)

# Filtros
st.sidebar.header("Filtros")
companies = st.sidebar.multiselect("Selecione as franquias:", df['Company'].unique(), default=df['Company'].unique())
df_filtered = df[df['Company'].isin(companies)]

# Métricas principais
st.markdown("### 🎯 Métricas Gerais")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Filmes", len(df_filtered))
col2.metric("ROI Médio", f"{df_filtered['ROI'].mean():.1%}")
col3.metric("Período", f"{int(df_filtered['Release'].min())} - {int(df_filtered['Release'].max())}")

# ROI médio por franquia
st.subheader("1️⃣ ROI Médio por Franquia")
roi_avg = df_filtered.groupby("Company")['ROI'].agg(['count', 'mean', 'min', 'max']).reset_index()
roi_avg.columns = ['Franquia', 'Total de Filmes', 'ROI Médio', 'Menor ROI', 'Maior ROI']
st.dataframe(roi_avg.style.format({'ROI Médio': '{:.1%}', 'Menor ROI': '{:.1%}', 'Maior ROI': '{:.1%}'}), use_container_width=True)

fig1 = px.bar(roi_avg, x='Franquia', y='ROI Médio', color='Franquia', text='ROI Médio')
st.plotly_chart(fig1, use_container_width=True)

# Top 5 maiores e menores ROI
st.subheader("2️⃣ Top 5 Maiores e Menores ROI")
col1, col2 = st.columns(2)
with col1:
    top5 = df_filtered.nlargest(5, 'ROI')[['Original_Title', 'Company', 'ROI', 'Budget', 'Gross_Worldwide']]
    st.markdown("### 🏆 Maiores ROI")
    st.dataframe(top5.style.format({'ROI': '{:.1%}', 'Budget': '${:,.0f}', 'Gross_Worldwide': '${:,.0f}'}), use_container_width=True)

with col2:
    bottom5 = df_filtered.nsmallest(5, 'ROI')[['Original_Title', 'Company', 'ROI', 'Budget', 'Gross_Worldwide']]
    st.markdown("### 😬 Menores ROI")
    st.dataframe(bottom5.style.format({'ROI': '{:.1%}', 'Budget': '${:,.0f}', 'Gross_Worldwide': '${:,.0f}'}), use_container_width=True)

# ROI por faixa de orçamento
st.subheader("3️⃣ ROI por Faixa de Orçamento")
roi_budget = df_filtered.groupby('Faixa_Orcamento').agg(
    qtd_filmes=('ROI', 'count'),
    ROI_medio=('ROI', 'mean'),
    Orcamento_medio=('Budget', 'mean')
).reset_index()

st.dataframe(roi_budget.style.format({'ROI_medio': '{:.1%}', 'Orcamento_medio': '${:,.0f}'}), use_container_width=True)

fig2 = px.bar(roi_budget, x='Faixa_Orcamento', y='ROI_medio', text='ROI_medio', color='Faixa_Orcamento')
st.plotly_chart(fig2, use_container_width=True)

# ROI por tipo de filme
st.subheader("4️⃣ ROI por Tipo de Filme")
roi_tipo = df_filtered.groupby(['Tipo_Filme', 'Company']).agg(ROI_medio=('ROI', 'mean'), Total=('ROI', 'count')).reset_index()

fig3 = px.bar(roi_tipo, x='Company', y='ROI_medio', color='Tipo_Filme', barmode='group', text='ROI_medio')
st.plotly_chart(fig3, use_container_width=True)

# Evolução ao longo do tempo
st.subheader("5️⃣ Evolução do ROI ao Longo dos Anos")
roi_time = df_filtered.groupby(['Release', 'Company'])['ROI'].mean().reset_index()
fig4 = px.line(roi_time, x='Release', y='ROI', color='Company', markers=True)
st.plotly_chart(fig4, use_container_width=True)

# Conclusão
st.markdown("---")
roi_final = roi_avg.sort_values("ROI Médio", ascending=False).iloc[0]
st.markdown(f"✅ A franquia com maior ROI médio é **{roi_final['Franquia']}**, com retorno de **{roi_final['ROI Médio']:.1%}**.")
