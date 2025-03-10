from dataclasses import dataclass 
from datetime import datetime
import pytz
from pathlib import Path
from typing import Optional

import yaml

from airflow.models.dag import DAG 
from airflow.decorators import task as airflow_task

DAGS_DIR = Path(__file__).parent
CONFIG_FILE = DAGS_DIR / "dags.yaml"
TASKS_DIR = DAGS_DIR / "tasks"

class ConfigFileLoadError(Exception):
    pass

@dataclass
class Task:
    id: str
    description: str
    requirements: list[str]
    file_path: str
    trigger_rule: Optional[str] = None
    
    def __post_init__(self):
        if not self.file_path:
            raise ConfigFileLoadError("")
        self.file_path = Path(TASKS_DIR) / self.file_path
        if not self.file_path.is_file():
            raise ConfigFileLoadError(f"File '{self.file_path}' not a file")


@dataclass
class Dag:
    id: str
    description: str
    start_date: datetime
    tasks: list[Task]
    schedule: Optional[str] = None

    def __post_init__(self):
        self.start_date = datetime(
            self.start_date.year,
            self.start_date.month,
            self.start_date.day,
        )
        if not self.tasks:
            raise ConfigFileLoadError("")
        if not type(self.tasks) == list:
            raise ConfigFileLoadError("")
        self.tasks = [ Task(**task_obj) for task_obj in self.tasks ]

@dataclass
class ConfigFile:
    dags: list[Dag]
    def __post_init__(self):
        if not self.dags:
            raise ConfigFileLoadError(f"No dags field found in configuration file '{config_file_path}'")
        if not type(self.dags) == list:
            raise ConfigFileLoadError(f"dags field in configuration file not of type list")
        self.dags = [ Dag(**dag_obj) for dag_obj in self.dags]

def run_file(params: dict):
    import traceback
    from pathlib import Path
    with Path(params.get("file_path")).open("r") as file:
        code = compile(file.read(), params.get("file_path"), "exec")
    try:
        exec(code)
    except Exception as e:
        traceback.print_exc()
        raise e

def load_config(file_path):
    with file_path.open('r') as file:
        data = yaml.safe_load(file)
    return ConfigFile(**data)


config = load_config(CONFIG_FILE)

for dag in config.dags:
    with DAG(
        dag.id,
        description=dag.description,
        start_date = dag.start_date,
        schedule=dag.schedule,
    ):
        tasks = None
        for task in dag.tasks:
            t = airflow_task.virtualenv(
                run_file,
                task_id=task.id,
                requirements=task.requirements,
                params={"file_path":str(task.file_path)},
                system_site_packages=True
            )()
            tasks = tasks >> t if tasks else t
        tasks


