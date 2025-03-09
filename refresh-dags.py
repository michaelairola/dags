from datetime import datetime, timedelta

from airflow.models.dag import DAG
from airflow.decorators import task

with DAG(
    "refresh-dags",
    description="Refresh the DAGS to be up to date",
    start_date=datetime(2025, 2, 11),
    catchup=False,
    schedule_interval=None,
) as dag:
    @task.virtualenv(
        task_id="git-pull",
        requirements=["GitPython"],
        system_site_packages=True
    )
    def refresh_dags():
        from pathlib import Path
        import logging
        import os
        from git import Repo

        logger = logging.getLogger(__name__)

        AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "~/airflow")
        remote = "origin"
        branch = "main"

        dags_dir = Path(AIRFLOW_HOME) / "dags"
        repo = Repo(dags_dir)
        
        logger.info(f"Pulling {repo}...")
        repo.remotes[remote].pull(branch)
        print(f"Successfully pulled changes from {remote}/{branch}")

    r = refresh_dags()

    r