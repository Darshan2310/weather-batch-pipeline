import requests
import psycopg2
import pandas as pd
from datetime import datetime
import json
import logging
import os

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.StreamHandler(),                     # prints to terminal
        logging.FileHandler("logs/pipeline.log")     # saves to log file
    ]
)
log = logging.getLogger(__name__)


# ── Config ─────────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "host.docker.internal",
    "database": "weather_db",
    "user":     "postgres",
    "password": "admin123",
    "port":     5433      
}

CITIES = [
    {"name": "Bhadravati",  "latitude": 19.8580, "longitude": 79.1542},
    {"name": "Mumbai",      "latitude": 19.0760, "longitude": 72.8777},
    {"name": "Pune",        "latitude": 18.5204, "longitude": 73.8567},
]

API_URL = "https://api.open-meteo.com/v1/forecast"


# ── Step 1 : Create table if it doesn't exist ──────────────────────────────────
def create_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS raw_weather (
        id                    SERIAL PRIMARY KEY,
        city                  VARCHAR(100),
        latitude              FLOAT,
        longitude             FLOAT,
        timestamp             TIMESTAMP,
        temperature_2m        FLOAT,
        relative_humidity_2m  FLOAT,
        precipitation         FLOAT,
        windspeed_10m         FLOAT,
        apparent_temperature  FLOAT,
        weathercode           INT,
        ingested_at           TIMESTAMP DEFAULT NOW()
    );
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    log.info("Table raw_weather is ready")


# ── Step 2 : Fetch data from Open-Meteo API ────────────────────────────────────
def fetch_weather(city: dict) -> dict:
    params = {
        "latitude":   city["latitude"],
        "longitude":  city["longitude"],
        "hourly":     "temperature_2m,relative_humidity_2m,precipitation,"
                      "windspeed_10m,apparent_temperature,weathercode",
        "timezone":   "Asia/Kolkata",
        "forecast_days": 7
    }
    log.info(f"Fetching weather for {city['name']} ...")
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()          # crashes loudly if API returns an error
    log.info(f"Got response for {city['name']} — status {response.status_code}")
    return response.json()


# ── Step 3 : Parse JSON into a clean list of rows ──────────────────────────────
def parse_weather(city: dict, raw: dict) -> list[dict]:
    hourly = raw["hourly"]
    rows = []

    for i, timestamp_str in enumerate(hourly["time"]):
        row = {
            "city":                  city["name"],
            "latitude":              city["latitude"],
            "longitude":             city["longitude"],
            "timestamp":             datetime.fromisoformat(timestamp_str),
            "temperature_2m":        hourly["temperature_2m"][i],
            "relative_humidity_2m":  hourly["relative_humidity_2m"][i],
            "precipitation":         hourly["precipitation"][i],
            "windspeed_10m":         hourly["windspeed_10m"][i],
            "apparent_temperature":  hourly["apparent_temperature"][i],
            "weathercode":           hourly["weathercode"][i],
        }
        rows.append(row)

    log.info(f"Parsed {len(rows)} rows for {city['name']}")
    return rows


# ── Step 4 : Insert rows into PostgreSQL ───────────────────────────────────────
def load_to_db(conn, rows: list[dict]):
    sql = """
    INSERT INTO raw_weather (
        city, latitude, longitude, timestamp,
        temperature_2m, relative_humidity_2m, precipitation,
        windspeed_10m, apparent_temperature, weathercode
    ) VALUES (
        %(city)s, %(latitude)s, %(longitude)s, %(timestamp)s,
        %(temperature_2m)s, %(relative_humidity_2m)s, %(precipitation)s,
        %(windspeed_10m)s, %(apparent_temperature)s, %(weathercode)s
    )
    ON CONFLICT DO NOTHING;
    """
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    conn.commit()
    log.info(f"Inserted {len(rows)} rows into raw_weather")


# ── Main orchestrator ──────────────────────────────────────────────────────────
def run_pipeline():
    log.info("========== Pipeline started ==========")

    # connect to database
    conn = psycopg2.connect(**DB_CONFIG)
    log.info("Connected to weather_db")

    # make sure the table exists
    create_table(conn)

    # loop through every city
    for city in CITIES:
        try:
            raw_data   = fetch_weather(city)
            rows       = parse_weather(city, raw_data)
            load_to_db(conn, rows)
        except Exception as e:
            log.error(f"Failed for {city['name']}: {e}")

    conn.close()
    log.info("========== Pipeline finished ==========")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_pipeline()