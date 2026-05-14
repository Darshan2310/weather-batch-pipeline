import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
# This must be the FIRST streamlit command in the file
st.set_page_config(
    page_title="Weather Pipeline Dashboard",
    page_icon="🌤️",
    layout="wide"
)

# ── Database config ────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "database": "weather_db",
    "user":     "postgres",
    "password": "admin123",   # <-- change this
    "port":     5433
}


# ── Helper : connect and run a query ──────────────────────────────────────────
# @st.cache_data tells Streamlit to remember the result for 10 minutes
# so it doesn't hit the database on every single click
@st.cache_data(ttl=600)
def run_query(sql: str) -> pd.DataFrame:
    """Connect to DB, run SQL, return a pandas DataFrame."""
    conn = psycopg2.connect(**DB_CONFIG)
    df   = pd.read_sql(sql, conn)
    conn.close()
    return df


# ── Load data from mart_daily_weather ─────────────────────────────────────────
@st.cache_data(ttl=600)
def load_daily_data() -> pd.DataFrame:
    sql = """
        SELECT
            city_name,
            weather_date,
            avg_temp_c,
            max_temp_c,
            min_temp_c,
            avg_feels_like_c,
            total_rainfall_mm,
            avg_windspeed_kmh,
            avg_humidity_pct,
            hours_of_data
        FROM mart_daily_weather
        ORDER BY city_name, weather_date
    """
    return run_query(sql)


@st.cache_data(ttl=600)
def load_hourly_data(city: str) -> pd.DataFrame:
    sql = f"""
        SELECT
            weather_hour,
            temperature_c,
            feels_like_c,
            humidity_pct,
            rainfall_mm,
            windspeed_kmh
        FROM stg_weather
        WHERE city_name = '{city}'
        ORDER BY weather_hour
    """
    return run_query(sql)


# ── Page header ────────────────────────────────────────────────────────────────
st.title("🌤️ Weather Pipeline Dashboard")
st.markdown("Real weather data — fetched from Open-Meteo API, "
            "stored in PostgreSQL, transformed with dbt.")
st.divider()


# ── Sidebar : city selector ────────────────────────────────────────────────────
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("Select a city to explore its weather data.")

cities     = ["Bhadravati", "Mumbai", "Pune"]
selected   = st.sidebar.selectbox("Choose a city", cities)
show_raw   = st.sidebar.checkbox("Show raw data table", value=False)

st.sidebar.divider()
st.sidebar.markdown("**Pipeline info**")
st.sidebar.markdown("- Source: Open-Meteo API")
st.sidebar.markdown("- Database: PostgreSQL 16")
st.sidebar.markdown("- Transform: dbt")
st.sidebar.markdown("- Dashboard: Streamlit")


# ── Load data ─────────────────────────────────────────────────────────────────
daily_df  = load_daily_data()
city_df   = daily_df[daily_df["city_name"] == selected].copy()
hourly_df = load_hourly_data(selected)


# ── Section 1 : Key metrics ────────────────────────────────────────────────────
st.subheader(f"📍 {selected} — Key Metrics")

# Get today's row or the latest available date
latest = city_df.iloc[-1] if not city_df.empty else None

if latest is not None:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        label="🌡️ Avg Temperature",
        value=f"{latest['avg_temp_c']}°C",
        delta=f"Feels like {latest['avg_feels_like_c']}°C"
    )
    col2.metric(
        label="💧 Avg Humidity",
        value=f"{latest['avg_humidity_pct']}%"
    )
    col3.metric(
        label="🌧️ Total Rainfall",
        value=f"{latest['total_rainfall_mm']} mm"
    )
    col4.metric(
        label="💨 Avg Wind Speed",
        value=f"{latest['avg_windspeed_kmh']} km/h"
    )

st.divider()


# ── Section 2 : Temperature trend ─────────────────────────────────────────────
st.subheader("🌡️ 7-Day Temperature Trend")
st.markdown("Average, maximum and minimum temperature per day.")

if not city_df.empty:
    temp_chart_df = city_df.set_index("weather_date")[
        ["avg_temp_c", "max_temp_c", "min_temp_c"]
    ]
    temp_chart_df.columns = ["Average °C", "Max °C", "Min °C"]
    st.line_chart(temp_chart_df)

st.divider()


# ── Section 3 : Rainfall bar chart ────────────────────────────────────────────
st.subheader("🌧️ Daily Rainfall")
st.markdown("Total rainfall in millimetres per day.")

if not city_df.empty:
    rain_df = city_df.set_index("weather_date")[["total_rainfall_mm"]]
    rain_df.columns = ["Rainfall (mm)"]
    st.bar_chart(rain_df)

st.divider()


# ── Section 4 : Hourly temperature today ──────────────────────────────────────
st.subheader("⏰ Hourly Temperature (Full 7 Days)")
st.markdown("Temperature reading for every hour across all 7 days.")

if not hourly_df.empty:
    hourly_temp = hourly_df.set_index("weather_hour")[["temperature_c"]]
    hourly_temp.columns = ["Temperature °C"]
    st.line_chart(hourly_temp)

st.divider()


# ── Section 5 : Compare all cities ────────────────────────────────────────────
st.subheader("🏙️ City Comparison — Average Temperature")
st.markdown("Side by side daily average temperature for all three cities.")

if not daily_df.empty:
    pivot_df = daily_df.pivot(
        index="weather_date",
        columns="city_name",
        values="avg_temp_c"
    )
    st.line_chart(pivot_df)

st.divider()


# ── Section 6 : Raw data table (optional) ─────────────────────────────────────
if show_raw:
    st.subheader("📋 Raw Daily Data")
    st.markdown("Full `mart_daily_weather` table for the selected city.")
    st.dataframe(
        city_df,
        use_container_width=True,
        hide_index=True
    )


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "Built with Python · PostgreSQL · dbt · Streamlit &nbsp;|&nbsp; "
    "Data from [Open-Meteo](https://open-meteo.com/) — free & open source",
    unsafe_allow_html=True
)