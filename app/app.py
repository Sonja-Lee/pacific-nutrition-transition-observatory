import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Pacific Nutrition Transition Observatory",
    page_icon="🌺",
    layout="wide"
)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "pacific_nutrition_transition_observatory.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

observatory = load_data()

st.title("Pacific Nutrition Transition Observatory")
st.subheader("Interactive Explorer")

st.write(
    "Explore nutrition transition, food systems, demographic change, and metabolic health "
    "across Pacific Island countries and territories."
)

st.sidebar.header("Explorer Controls")

selected_country = st.sidebar.selectbox(
    "Select country",
    sorted(observatory["Country"].unique())
)

country_data = observatory[observatory["Country"] == selected_country].sort_values("Year")
latest = country_data.iloc[-1]

st.header(selected_country)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Latest year", int(latest["Year"]))
col2.metric("Population", f"{latest['Population']:,.0f}")
col3.metric("Obesity", f"{latest['Obesity_Pct']:.1f}%")

if pd.notna(latest["Diabetes_Pct"]):
    col4.metric("Diabetes", f"{latest['Diabetes_Pct'] * 100:.1f}%")
else:
    col4.metric("Diabetes", "Unavailable")

st.divider()

st.subheader("Dataset Preview")

st.write(f"Rows: {observatory.shape[0]}")
st.write(f"Columns: {observatory.shape[1]}")
st.write(f"Countries: {observatory['Country'].nunique()}")
st.write(f"Years: {observatory['Year'].min()} to {observatory['Year'].max()}")

st.dataframe(observatory.head())
