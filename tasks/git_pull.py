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
