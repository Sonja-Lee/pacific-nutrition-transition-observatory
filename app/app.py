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

def latest_value(data, column, multiplier=1, is_percent=False):
    valid = data[["Year", column]].dropna()

    if valid.empty:
        return "No data", ""

    row = valid.sort_values("Year").iloc[-1]
    value = row[column] * multiplier
    year = int(row["Year"])

    if is_percent:
        return f"{value:.1f}%", f"latest: {year}"
    else:
        return f"{int(value):,}", f"latest: {year}"

population_value, population_year = latest_value(country_df, "Population")
obesity_value, obesity_year = latest_value(country_df, "Obesity_Pct", is_percent=True)
diabetes_value, diabetes_year = latest_value(country_df, "Diabetes_Pct", multiplier=100, is_percent=True)
hypertension_value, hypertension_year = latest_value(country_df, "Hypertension_Pct", multiplier=100, is_percent=True)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Population", population_value, population_year)
col2.metric("Obesity", obesity_value, obesity_year)
col3.metric("Diabetes", diabetes_value, diabetes_year)
col4.metric("Hypertension", hypertension_value, hypertension_year)

st.divider()

st.subheader("Dataset Preview")

st.write(f"Rows: {observatory.shape[0]}")
st.write(f"Columns: {observatory.shape[1]}")
st.write(f"Countries: {observatory['Country'].nunique()}")
st.write(f"Years: {observatory['Year'].min()} to {observatory['Year'].max()}")

st.dataframe(observatory.head())