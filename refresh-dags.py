from datetime import datetime, timedelta
from pathlib import Path

import git

from airflow.models.dag import DAG
from airflow.decorators import task

with DAG(
    "refresh-dags",
    description="Refresh the DAGS to be up to date",
    schedule=timedelta(days=1),
    start_date=datetime(2025, 2, 11),
    catchup=False,
    tags=["airflow"],
) as dag:

    @task(task_id="refresh_dags")
    def refresh_dags():
        dags_dir = Path(__file__).parent
        print(f"Pulling {dags_dir}...")
        g = git.cmd.Git(dags_dir)
        g.pull()
    
    r = refresh_dags()

    r