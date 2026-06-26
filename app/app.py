import streamlit as st
import pandas as pd
import plotly.express as px
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

def latest_value(data, column, multiplier=1, is_percent=False, decimals=1):
    valid = data[["Year", column]].dropna()
    if valid.empty:
        return "No data", ""
    row = valid.sort_values("Year").iloc[-1]
    value = row[column] * multiplier
    year = int(row["Year"])
    if is_percent:
        return f"{value:.{decimals}f}%", f"latest: {year}"
    if abs(value) >= 1000:
        return f"{value:,.0f}", f"latest: {year}"
    return f"{value:.{decimals}f}", f"latest: {year}"

def latest_country_values(data, x_col, y_col, x_multiplier=1, y_multiplier=1):
    rows = []
    for country in sorted(data["Country"].dropna().unique()):
        cdf = data[data["Country"] == country]
        x_valid = cdf[["Year", x_col]].dropna()
        y_valid = cdf[["Year", y_col]].dropna()
        if x_valid.empty or y_valid.empty:
            continue

        x_row = x_valid.sort_values("Year").iloc[-1]
        y_row = y_valid.sort_values("Year").iloc[-1]

        rows.append({
            "Country": country,
            "X value": x_row[x_col] * x_multiplier,
            "Y value": y_row[y_col] * y_multiplier,
            "X year": int(x_row["Year"]),
            "Y year": int(y_row["Year"])
        })
    return pd.DataFrame(rows)

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

insights_tab, overview_tab, food_tab, relationship_tab, rankings_tab, data_tab = st.tabs(
    ["Key Insights", "Overview", "Food Systems", "Relationships", "Rankings", "Data"]
)

with insights_tab:
    st.header("Key Insights")

    st.write(
        "This section highlights the most significant observable patterns and relationships between food"
            "systems, nutrition, and metabolic health across Pacific Island countries and territories."
    )
    
    st.subheader("Top current metabolic health signals")

    def latest_table(data, column, multiplier=1):
        rows = []
        for country in sorted(data["Country"].dropna().unique()):
            cdf = data[data["Country"] == country]
            valid = cdf[["Year", column]].dropna()
            if valid.empty:
                continue
            row = valid.sort_values("Year").iloc[-1]
            rows.append({
                "Country": country,
                "Value": row[column] * multiplier,
                "Latest year": int(row["Year"])
            })
        return pd.DataFrame(rows).sort_values("Value", ascending=False).reset_index(drop=True)

    obesity_rank = latest_table(observatory, "Obesity_Pct", 1)
    diabetes_rank = latest_table(observatory, "Diabetes_Pct", 100)
    dietary_energy_rank = latest_table(observatory, "Dietary_Energy_kcal", 1)

    col1, col2, col3 = st.columns(3)

    if not obesity_rank.empty:
        top = obesity_rank.iloc[0]
        col1.metric(
            "Highest obesity",
            f"{top['Country']}",
            f"{top['Value']:.1f}% in {int(top['Latest year'])}"
        )

    if not diabetes_rank.empty:
        top = diabetes_rank.iloc[0]
        col2.metric(
            "Highest diabetes",
            f"{top['Country']}",
            f"{top['Value']:.1f}% in {int(top['Latest year'])}"
        )

    if not dietary_energy_rank.empty:
        top = dietary_energy_rank.iloc[0]
        col3.metric(
            "Highest dietary energy supply",
            f"{top['Country']}",
            f"{top['Value']:,.0f} kcal/day in {int(top['Latest year'])}"
        )

    st.subheader("Food system vs health relationships")

    relationship_checks = {
        "Dietary energy vs obesity": ("Dietary_Energy_kcal", "Obesity_Pct", 1, 1),
        "Fat supply vs obesity": ("Fat_g", "Obesity_Pct", 1, 1),
        "Food imports vs obesity": ("Food_Imports_Export_Value_Pct", "Obesity_Pct", 1, 1),
        "Food imports vs diabetes": ("Food_Imports_Export_Value_Pct", "Diabetes_Pct", 1, 100),
    }

    relationship_rows = []

    for label, (x_col, y_col, x_mult, y_mult) in relationship_checks.items():
        rel = latest_country_values(observatory, x_col, y_col, x_mult, y_mult)
        if len(rel) >= 3:
            relationship_rows.append({
                "Relationship": label,
                "Countries with data": len(rel),
                "Pearson r": rel["X value"].corr(rel["Y value"])
            })

    relationship_df = pd.DataFrame(relationship_rows)

    if relationship_df.empty:
        st.warning("Not enough overlapping data to calculate relationship signals.")
    else:
        relationship_df = relationship_df.sort_values("Pearson r", ascending=False)
        strongest = relationship_df.iloc[0]

    st.info(
        f"""
    ### Observatory Insight

    Across Pacific Island jurisdictions with overlapping data,
    **{strongest['Relationship']}** currently shows the strongest
    positive relationship observed in this dataset.

    Pearson correlation: **r = {strongest['Pearson r']:.2f}**, based on **{int(strongest['Countries with data'])} countries**.

    This relationship is exploratory rather than causal, but it identifies
    a pattern that warrants closer investigation.
    """
    )
        
    st.dataframe(relationship_df, use_container_width=True)

    st.subheader("Interpretation caution")

    st.write(
        "These patterns are exploratory. The dashboard combines multiple source "
        "datasets with different reporting years and uneven country coverage. The value here "
        "is not a final conclusion; it is a faster way to identify which relationships deserve "
        "closer inspection.\n\n"
        "The purpose of this observatory is not to prove causation. It is to rapidly surface "
        "meaningful patterns and relationships across Pacific food systems and metabolic health "
        "so they can be investigated further."
    )

with overview_tab:
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
    trend_data = trend_data.rename(columns={
        "Obesity_Pct": "Obesity",
        "Diabetes_Pct": "Diabetes",
        "Hypertension_Pct": "Hypertension"
    })

    fig = px.line(
        trend_data,
        x="Year",
        y=["Obesity", "Diabetes", "Hypertension"],
        labels={"value": "Percent", "variable": "Indicator"},
        title=f"Metabolic health trends: {selected_country}"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Metric cards show the latest available non-missing value for each indicator. "
        "Years may differ because source datasets are updated on different schedules."
    )

with food_tab:
    st.header(f"Food System Indicators: {selected_country}")

    energy_value, energy_year = latest_value(country_data, "Dietary_Energy_kcal", decimals=0)
    fat_value, fat_year = latest_value(country_data, "Fat_g")
    protein_value, protein_year = latest_value(country_data, "Protein_g")
    import_value, import_year = latest_value(country_data, "Food_Imports_Export_Value_Pct", is_percent=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dietary energy", energy_value, energy_year)
    col2.metric("Fat supply", fat_value, fat_year)
    col3.metric("Protein supply", protein_value, protein_year)
    col4.metric("Food imports", import_value, import_year)

    food_trend = country_data[[
        "Year",
        "Dietary_Energy_kcal",
        "Fat_g",
        "Protein_g",
        "Food_Imports_Export_Value_Pct"
    ]].copy()

    food_trend = food_trend.rename(columns={
        "Dietary_Energy_kcal": "Dietary energy kcal/cap/day",
        "Fat_g": "Fat supply g/cap/day",
        "Protein_g": "Protein supply g/cap/day",
        "Food_Imports_Export_Value_Pct": "Food imports % of merchandise exports"
    })

    fig = px.line(
        food_trend,
        x="Year",
        y=[
            "Dietary energy kcal/cap/day",
            "Fat supply g/cap/day",
            "Protein supply g/cap/day",
            "Food imports % of merchandise exports"
        ],
        labels={"value": "Reported value", "variable": "Indicator"},
        title=f"Food system trends: {selected_country}"
    )
    st.plotly_chart(fig, use_container_width=True)

with relationship_tab:
    st.header("Food System and Health Relationships")

    x_options = {
        "Dietary energy kcal/cap/day": ("Dietary_Energy_kcal", 1),
        "Fat supply g/cap/day": ("Fat_g", 1),
        "Protein supply g/cap/day": ("Protein_g", 1),
        "Food imports % of merchandise exports": ("Food_Imports_Export_Value_Pct", 1)
    }

    y_options = {
        "Obesity %": ("Obesity_Pct", 1),
        "Diabetes %": ("Diabetes_Pct", 100),
        "Hypertension %": ("Hypertension_Pct", 100)
    }

    col1, col2 = st.columns(2)
    x_label = col1.selectbox("Food system indicator", list(x_options.keys()))
    y_label = col2.selectbox("Health outcome", list(y_options.keys()))

    x_col, x_mult = x_options[x_label]
    y_col, y_mult = y_options[y_label]

    rel = latest_country_values(observatory, x_col, y_col, x_mult, y_mult)

    if len(rel) < 3:
        st.warning("Not enough countries have overlapping data for a reliable scatterplot.")
        st.dataframe(rel, use_container_width=True)
    else:
        corr = rel["X value"].corr(rel["Y value"])
        fig = px.scatter(
            rel,
            x="X value",
            y="Y value",
            text="Country",
            hover_data=["Country", "X year", "Y year"],
            labels={"X value": x_label, "Y value": y_label},
            title=f"{x_label} vs {y_label} across Pacific jurisdictions"
        )
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Pearson correlation", f"{corr:.2f}")
        st.caption("Each point uses the latest available non-missing value for each country and indicator.")

with rankings_tab:
    st.header("Latest Available Rankings")

    ranking_options = {
        "Obesity %": ("Obesity_Pct", 1),
        "Diabetes %": ("Diabetes_Pct", 100),
        "Hypertension %": ("Hypertension_Pct", 100),
        "Dietary energy kcal/cap/day": ("Dietary_Energy_kcal", 1),
        "Food imports % of merchandise exports": ("Food_Imports_Export_Value_Pct", 1),
        "Population": ("Population", 1),
        "Median age": ("Median_Age", 1)
    }

    ranking_label = st.selectbox("Ranking indicator", list(ranking_options.keys()))
    ranking_col, ranking_mult = ranking_options[ranking_label]

    ranking_rows = []
    for country in countries:
        cdf = observatory[observatory["Country"] == country]
        valid = cdf[["Year", ranking_col]].dropna()
        if valid.empty:
            continue
        row = valid.sort_values("Year").iloc[-1]
        ranking_rows.append({
            "Country": country,
            "Value": row[ranking_col] * ranking_mult,
            "Latest year": int(row["Year"])
        })

    ranking_df = pd.DataFrame(ranking_rows).sort_values("Value", ascending=False).reset_index(drop=True)
    ranking_df.index = ranking_df.index + 1
    st.dataframe(ranking_df, use_container_width=True)

with data_tab:
    st.header("Dataset Summary")

    st.write(f"Rows: {observatory.shape[0]}")
    st.write(f"Columns: {observatory.shape[1]}")
    st.write(f"Countries and territories: {observatory['Country'].nunique()}")
    st.write(f"Years: {observatory['Year'].min()} to {observatory['Year'].max()}")

    with st.expander("Show first rows of dataset"):
        st.dataframe(observatory.head(), use_container_width=True)
