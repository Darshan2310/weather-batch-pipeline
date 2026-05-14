from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import subprocess

# ── Default settings ───────────────────────────────────────────────────────────
default_args = {
    "owner":            "you",
    "retries":          1,
    "retry_delay":      timedelta(minutes=5),
    "email_on_failure": False,
}

# ── Import your ingestion function ─────────────────────────────────────────────
sys.path.insert(0, "/opt/airflow/src/ingestion")
from extract import run_pipeline


# ── dbt runner functions ───────────────────────────────────────────────────────
def run_dbt_run():
    """Run dbt models using exact executable path."""
    result = subprocess.run(
        [
            "/home/airflow/.local/bin/dbt",
            "run",
            "--project-dir", "/opt/airflow/weather_pipeline",
            "--profiles-dir", "/opt/airflow/weather_pipeline"
        ],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print(result.stderr)
    if result.returncode != 0:
        raise Exception(f"dbt run failed:\n{result.stderr}")


def run_dbt_test():
    """Run dbt tests using exact executable path."""
    result = subprocess.run(
        [
            "/home/airflow/.local/bin/dbt",
            "test",
            "--project-dir", "/opt/airflow/weather_pipeline",
            "--profiles-dir", "/opt/airflow/weather_pipeline"
        ],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print(result.stderr)
    if result.returncode != 0:
        raise Exception(f"dbt test failed:\n{result.stderr}")


# ── Define the DAG ─────────────────────────────────────────────────────────────
with DAG(
    dag_id="weather_pipeline",
    default_args=default_args,
    description="Fetch weather → load to DB → transform with dbt",
    schedule_interval="0 6 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["weather", "portfolio"],
) as dag:

    # Task 1 — Extract and Load
    extract_load = PythonOperator(
        task_id="extract_and_load",
        python_callable=run_pipeline,
    )

    # Task 2 — dbt run
    dbt_run = PythonOperator(
        task_id="dbt_run",
        python_callable=run_dbt_run,
    )

    # Task 3 — dbt test
    dbt_test = PythonOperator(
        task_id="dbt_test",
        python_callable=run_dbt_test,
    )

    # Pipeline order
    extract_load >> dbt_run >> dbt_test