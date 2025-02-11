
import textwrap
from datetime import datetime, timedelta
from pathlib import Path
import os

# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG
from airflow.decorators import task


# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
with DAG(
    "refresh-dags",
    description="Refresh the DAGS to be up to date",
    schedule=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["airflow"],
) as dag:

    @task(task_id="refresh_dags")
    def refresh_dags():
        dags_dir = Path(__file__).parent
        print("dags directory is:", dags_dir)
    
    r = refresh_dags()

    r