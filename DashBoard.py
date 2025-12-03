import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="COVID-19 Analytics Dashboard", layout="wide")

# ---------------------------
# Load Country List (small + safe)
# ---------------------------
@st.cache_data
def load_country_list():
    url = "https://covid.ourworldindata.org/v1/owid-covid-latest.json"
    latest = pd.read_json(url)
    return sorted(latest.columns.tolist())


# ---------------------------
# Load Timeseries Data (per-country API)
# ---------------------------
@st.cache_data
def load_country_data(country):
    url = f"https://covid.ourworldindata.org/v1/country/{country}.csv"
    df = pd.read_csv(url, parse_dates=["date"])
    return df


# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.header("Filters")

countries = load_country_list()

default_index = countries.index("IND") if "IND" in countries else 0
selected_country = st.sidebar.selectbox("Select Country", countries, index=default_index)

metric = st.sidebar.selectbox(
    "Select Metric",
    [
        "new_cases", "total_cases", "new_deaths", "total_deaths",
        "people_vaccinated", "new_vaccinations",
    ],
)

# ---------------------------
# Load Country Time-Series
# ---------------------------
country_data = load_country_data(selected_country).sort_values("date")

st.title("COVID-19 Analytics Dashboard")
st.caption("Powered by Streamlit — OWID Per-Country API (Optimized for Cloud Hosting)")

# ---------------------------
# KPIs
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

latest = country_data.iloc[-1]

col1.metric("Total Cases", f"{latest.get('total_cases', 0):,.0f}")
col2.metric("Total Deaths", f"{latest.get('total_deaths', 0):,.0f}")

# Vaccination (avoid NaN)
people_vax = latest.get("people_vaccinated", 0)
if pd.isna(people_vax):
    people_vax = 0

col3.metric("People Vaccinated", f"{people_vax:,.0f}")

# Tests (fallback to 0)
tests = latest.get("total_tests", 0)
if pd.isna(tests):
    tests = 0

col4.metric("Total Tests", f"{tests:,.0f}")

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
