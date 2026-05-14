# 🌤️ Weather Batch Pipeline

An end-to-end data engineering portfolio project that automatically fetches 
real weather data for Indian cities, stores it in a database, transforms it 
with dbt, schedules it with Airflow, and visualises it in a live dashboard.

---

## 📐 Architecture
Open-Meteo API (free weather data)
↓
Python Ingestion Script
↓
PostgreSQL 16 (raw_weather table)
↓
dbt Transformations
├── stg_weather (view — cleaned data)
└── mart_daily_weather (table — daily summaries)
↓
Apache Airflow DAG (scheduled 6am daily)
↓
Streamlit Dashboard (live charts)

---

## 🛠️ Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Extraction | Python + Requests | Fetch weather data from REST API |
| Storage | PostgreSQL 16 | Store raw and transformed data |
| Transformation | dbt Core 1.8 | Clean, model and test data |
| Orchestration | Apache Airflow 2.8 | Schedule and monitor pipeline |
| Containerisation | Docker + Docker Compose | Run Airflow in isolated containers |
| Visualisation | Streamlit | Interactive dashboard |

---

## 📊 Data Source

[Open-Meteo API](https://open-meteo.com/) — free, no API key required.

Cities tracked:
- Bhadravati, Maharashtra
- Mumbai, Maharashtra  
- Pune, Maharashtra

Weather variables collected every hour:
- Temperature (°C) and feels-like temperature
- Relative humidity (%)
- Precipitation / rainfall (mm)
- Wind speed (km/h)
- Weather code

Pipeline collects 7 days of hourly data = **168 rows per city per run**.

---

## 🗂️ Project Structure
weather-batch-pipeline/
│
├── src/
│   └── ingestion/
│       └── extract.py          # Python ingestion script
│
├── weather_pipeline/           # dbt project
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_weather.sql
│   │   │   └── stg_weather.yml
│   │   └── marts/
│   │       └── mart_daily_weather.sql
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── airflow/
│   ├── dags/
│   │   └── weather_pipeline_dag.py   # Airflow DAG
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── dashboard/
│   └── app.py                  # Streamlit dashboard
│
├── logs/                       # Pipeline logs
├── .gitignore
└── README.md

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10
- PostgreSQL 16
- Docker Desktop

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/weather-batch-pipeline.git
cd weather-batch-pipeline
```

### 2. Set up Python environment
```bash
python -m venv venv
venv\Scripts\activate
pip install requests psycopg2-binary pandas streamlit dbt-postgres
```

### 3. Set up PostgreSQL
- Create a database called `weather_db`
- Note your PostgreSQL port (default 5432)

### 4. Configure credentials
Update the `DB_CONFIG` in these files with your PostgreSQL password:
- `src/ingestion/extract.py`
- `dashboard/app.py`
- `weather_pipeline/profiles.yml`

### 5. Run the ingestion script
```bash
python src/ingestion/extract.py
```

### 6. Run dbt transformations
```bash
cd weather_pipeline
dbt run
dbt test
```

### 7. Start the Streamlit dashboard
```bash
cd ..
streamlit run dashboard/app.py
```
Open `http://localhost:8501` in your browser.

### 8. Start Airflow (optional — for scheduling)
```bash
cd airflow
docker compose up -d
```
Open `http://localhost:8080` — login with `admin/admin`

---

## 📈 Dashboard Features

- **Key metrics** — latest temperature, humidity, rainfall, wind speed
- **7-day temperature trend** — avg, max, min per day
- **Daily rainfall chart** — total precipitation per day
- **Hourly temperature** — every hour across 7 days
- **City comparison** — all 3 cities on one chart
- **Raw data table** — toggle on/off from sidebar

---

## 🧪 Data Quality Tests

dbt runs 5 automated tests on every pipeline execution:

| Test | Column | Rule |
|---|---|---|
| unique | weather_id | No duplicate rows |
| not_null | weather_id | ID always present |
| not_null | city_name | City always present |
| not_null | temperature_c | Temperature always present |
| accepted_values | city_name | Only valid cities |

---

## 📅 Pipeline Schedule

The Airflow DAG runs automatically every day at 6:00 AM IST.

Each run:
1. Fetches fresh 7-day forecast for all 3 cities
2. Loads raw data into PostgreSQL
3. Rebuilds dbt models
4. Runs all data quality tests

---

## 💡 Key Learnings

- Building ELT pipelines with Python and REST APIs
- Data modelling with dbt (staging → mart pattern)
- Writing data quality tests as code
- Containerising workflows with Docker
- Orchestrating pipelines with Airflow DAGs
- Building data dashboards with Streamlit

---

## 👤 Author

**Darshan Chauhan**  
Analytics Consultant  
[LinkedIn](https://linkedin.com/in/darshan-chauhan-60037822a) | [GitHub](https://github.com/Darshan2310)