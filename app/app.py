import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Pacific Nutrition Transition Observatory",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "pacific_nutrition_transition_observatory.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

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

observatory = load_data()

st.title("Pacific Nutrition Transition Observatory")
st.subheader("Interactive Explorer")

st.write(
    "Explore nutrition transition, food systems, demographic change, and metabolic health "
    "across Pacific Island countries and territories."
)

countries = sorted(observatory["Country"].dropna().unique())
default_country = "Fiji"
default_index = countries.index(default_country) if default_country in countries else 0

selected_country = st.selectbox(
    "Select a country or territory",
    countries,
    index=default_index
)

country_data = observatory[observatory["Country"] == selected_country].sort_values("Year")

st.header(selected_country)

population_value, population_year = latest_value(country_data, "Population")
obesity_value, obesity_year = latest_value(country_data, "Obesity_Pct", is_percent=True)
diabetes_value, diabetes_year = latest_value(country_data, "Diabetes_Pct", multiplier=100, is_percent=True)
hypertension_value, hypertension_year = latest_value(country_data, "Hypertension_Pct", multiplier=100, is_percent=True)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Population", population_value, population_year)
col2.metric("Obesity", obesity_value, obesity_year)
col3.metric("Diabetes", diabetes_value, diabetes_year)
col4.metric("Hypertension", hypertension_value, hypertension_year)

st.divider()

st.subheader("Metabolic Health Trends")

trend_data = country_data[["Year", "Obesity_Pct", "Diabetes_Pct", "Hypertension_Pct"]].copy()
trend_data["Diabetes_Pct"] = trend_data["Diabetes_Pct"] * 100
trend_data["Hypertension_Pct"] = trend_data["Hypertension_Pct"] * 100

trend_data = trend_data.rename(
    columns={
        "Obesity_Pct": "Obesity",
        "Diabetes_Pct": "Diabetes",
        "Hypertension_Pct": "Hypertension"
    }
)

st.line_chart(
    trend_data.set_index("Year")[["Obesity", "Diabetes", "Hypertension"]]
)

st.caption(
    "Metric cards show the latest available non-missing value for each indicator. "
    "Years may differ because source datasets are updated on different schedules."
)

st.divider()

st.subheader("Dataset Preview")

st.write(f"Rows: {observatory.shape[0]}")
st.write(f"Columns: {observatory.shape[1]}")
st.write(f"Countries and territories: {observatory['Country'].nunique()}")
st.write(f"Years: {observatory['Year'].min()} to {observatory['Year'].max()}")

with st.expander("Show first rows of dataset"):
    st.dataframe(observatory.head(), use_container_width=True)
