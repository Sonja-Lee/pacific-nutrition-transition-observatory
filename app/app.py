import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Pacific Nutrition Transition Observatory",
    page_icon="🌺",
    layout="wide"
)

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "processed" / "pacific_nutrition_transition_observatory.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

df = load_data()

st.title("Pacific Nutrition Transition Observatory")
st.caption("Nutrition transition and noncommunicable disease explorer")

countries = sorted(df["Country"].dropna().unique())

default_country = "Fiji"
default_index = countries.index(default_country) if default_country in countries else 0

country = st.sidebar.selectbox(
    "Country",
    countries,
    index=default_index
)

country_df = df[df["Country"] == country].sort_values("Year")

st.header(country)

latest = country_df.iloc[-1]

def pct(value, multiplier=1):
    if pd.isna(value):
        return "No data"
    return f"{value * multiplier:.1f}%"

def number(value):
    if pd.isna(value):
        return "No data"
    return f"{int(value):,}"

col1, col2, col3, col4 = st.columns(4)

col1.metric("Population", number(latest["Population"]))
col2.metric("Obesity", pct(latest["Obesity_Pct"]))
col3.metric("Diabetes", pct(latest["Diabetes_Pct"], 100))
col4.metric("Hypertension", pct(latest["Hypertension_Pct"], 100))

st.divider()

indicator_names = {
    "Obesity (%)": ("Obesity_Pct", 1),
    "Diabetes (%)": ("Diabetes_Pct", 100),
    "Hypertension (%)": ("Hypertension_Pct", 100),
    "Dietary Energy (kcal)": ("Dietary_Energy_kcal", 1),
    "Food Imports (% GDP)": ("Food_Imports_Export_Value_Pct", 1),
    "Population": ("Population", 1),
    "Median Age": ("Median_Age", 1)
}

indicator = st.selectbox(
    "Indicator",
    list(indicator_names.keys())
)

column, multiplier = indicator_names[indicator]

plot_df = country_df[["Year", column]].copy()

if multiplier != 1:
    plot_df[column] = plot_df[column] * multiplier

st.line_chart(plot_df.set_index("Year"))

st.divider()

st.subheader("Latest Rankings")

ranking = (
    df[df["Year"] == df["Year"].max()][["Country", column]]
    .dropna()
    .sort_values(column, ascending=False)
)

if multiplier != 1:
    ranking[column] = ranking[column] * multiplier

st.dataframe(ranking, use_container_width=True)

st.divider()

with st.expander("Preview Dataset"):
    st.dataframe(df.head(), use_container_width=True)