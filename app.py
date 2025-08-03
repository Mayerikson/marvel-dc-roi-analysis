import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv("db.csv")
# Tente com latin1 primeiro
try:
    df = pd.read_csv("db.csv", encoding="latin1")
except UnicodeDecodeError:

# Remove unnamed column if exists
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Remove rows with missing publisher or appearances
df = df.dropna(subset=["publisher", "APPEARANCES"])
df = df[df["publisher"].isin(["Marvel", "DC"])]

# Convert APPEARANCES to numeric
df["APPEARANCES"] = pd.to_numeric(df["APPEARANCES"], errors="coerce")

st.set_page_config(page_title="Marvel vs DC Dashboard", layout="wide")

st.title("📊 Marvel vs DC Comics Dashboard")
st.markdown("A comparison of characters from **Marvel** and **DC** based on appearance data and attributes.")

# Sidebar filters
st.sidebar.header("Filters")
min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (1960, 2020))
alignment = st.sidebar.multiselect("Character Alignment", options=df["ALIGN"].dropna().unique(), default=df["ALIGN"].dropna().unique())

# Filter data
df_filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
if alignment:
    df_filtered = df_filtered[df_filtered["ALIGN"].isin(alignment)]

# Layout: 2 columns
col1, col2 = st.columns(2)

with col1:
    appearances_plot = df_filtered.groupby("publisher")["APPEARANCES"].sum().reset_index()
    fig1 = px.bar(appearances_plot, x="publisher", y="APPEARANCES", color="publisher",
                  title="Total Appearances by Publisher", text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    count_plot = df_filtered["publisher"].value_counts().reset_index()
    count_plot.columns = ["publisher", "Count"]
    fig2 = px.pie(count_plot, names="publisher", values="Count", title="Character Count by Publisher")
    st.plotly_chart(fig2, use_container_width=True)

# Additional insights
st.subheader("🧬 Character Attributes")

tab1, tab2, tab3 = st.tabs(["Eye Color", "Hair Color", "Sex"])

with tab1:
    eye_plot = df_filtered.groupby(["publisher", "EYE"]).size().reset_index(name="count")
    fig3 = px.bar(eye_plot, x="EYE", y="count", color="publisher", barmode="group",
                  title="Eye Color Distribution")
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    hair_plot = df_filtered.groupby(["publisher", "HAIR"]).size().reset_index(name="count")
    fig4 = px.bar(hair_plot, x="HAIR", y="count", color="publisher", barmode="group",
                  title="Hair Color Distribution")
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    sex_plot = df_filtered.groupby(["publisher", "SEX"]).size().reset_index(name="count")
    fig5 = px.bar(sex_plot, x="SEX", y="count", color="publisher", barmode="group",
                  title="Sex Distribution")
    st.plotly_chart(fig5, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Developed by [Your Name]. Data source: [FiveThirtyEight](https://github.com/fivethirtyeight/data/tree/master/comic-characters)")
