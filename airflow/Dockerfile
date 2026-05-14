FROM apache/airflow:2.8.1-python3.10

USER root

# Install PostgreSQL dev libraries so psycopg2 can compile if needed
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install all Python packages cleanly in one layer
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    requests \
    pandas \
    psycopg2-binary==2.9.9 \
    dbt-postgres==1.8.0