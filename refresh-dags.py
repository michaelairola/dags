from datetime import datetime, timedelta

from airflow.models.dag import DAG
from airflow.decorators import task

with DAG(
    "refresh-dags",
    description="Refresh the DAGS to be up to date",
    start_date=datetime(2025, 2, 11),
    catchup=False,
    schedule_interval=None,
    tags=["airflow"],
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
        logger = logging.getLogger(__name__)

        import git

        AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "~/airflow")

        dags_dir = Path(AIRFLOW_HOME) / "dags"
        logger.info(f"Pulling {dags_dir}...")
        g = git.cmd.Git(dags_dir)
        return g.pull()
    
    r = refresh_dags()

    r