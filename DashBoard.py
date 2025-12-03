import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="COVID-19 Analytics Dashboard", layout="wide")

# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    url = "https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv"
    df = pd.read_csv(url, parse_dates=["date"], low_memory=False)
    return df

df = load_data()

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.header("Filters")

countries = sorted(df["country"].dropna().unique())

default_index = countries.index("India") if "India" in countries else 0
selected_country = st.sidebar.selectbox("Select Country", countries, index=default_index)

metric = st.sidebar.selectbox(
    "Select Metric",
    [
        "new_cases", "total_cases", "new_deaths", "total_deaths",
        "people_vaccinated", "new_vaccinations",
    ],
)

# ---------------------------
# Country Data
# ---------------------------
country_data = df[df["country"] == selected_country].sort_values("date")

st.title("COVID-19 Analytics Dashboard")
st.caption("Powered by Streamlit — uses OWID Compact COVID Dataset")

# ---------------------------
# KPIs
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

latest = country_data.iloc[-1]

col1.metric("Total Cases", f"{latest.get('total_cases', 0):,.0f}")
col2.metric("Total Deaths", f"{latest.get('total_deaths', 0):,.0f}")
col3.metric("People Vaccinated", f"{latest.get('people_vaccinated', 0):,.0f}")
col4.metric("Total Tests", f"{latest.get('total_tests', 0):,}" if "total_tests" in country_data.columns else "0")

# ---------------------------
# Line Chart
# ---------------------------
st.subheader(f"{metric.replace('_',' ').title()} Over Time — {selected_country}")

fig = px.line(
    country_data,
    x="date",
    y=metric,
    title=f"{metric.replace('_',' ').title()} Trend in {selected_country}",
)
st.plotly_chart(fig, use_container_width=True)



# ---------------------------
# Correlation Heatmap
# ---------------------------
st.subheader("Correlation Heatmap — Country Level")

corr_cols = [
    "total_cases", "total_deaths",
    "people_vaccinated", "new_cases", "new_deaths",
]

available_cols = [c for c in corr_cols if c in country_data.columns]

if len(available_cols) >= 2:
    cor_df = country_data[available_cols].corr()

    heatmap = px.imshow(
        cor_df,
        text_auto=True,
        aspect="auto",
        title="Correlation Matrix"
    )
    st.plotly_chart(heatmap, use_container_width=True)

else:
    st.info("Not enough numeric columns available for correlation matrix.")

# ---------------------------
# Notes
# ---------------------------
st.info("""
To run this dashboard locally:

Run:
    streamlit run DashBoard.py
""")
