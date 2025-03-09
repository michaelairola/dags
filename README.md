
# 
grep1() { awk -v pattern="${1:?pattern is empty}" 'NR==1 || $0~pattern' "${2:-/dev/stdin}"; }
sudo systemctl list-unit-files | grep1 airflow 

# on UBUNTU machine, run this to attempt to develop
sudo systemctl stop airflow-scheduler airflow-ui

# shows that the scheduler runs `airflow/.venv/bin/airflow scheduler`
sudo systemctl show airflow-scheduler

# reset airflow 

rm -rf .venv;
python3 -m venv .venv;
source ./venv/bin/activate;
pip install 'apache-airflow[virtualenv]';
pip install psycopg2-binary;
pip install cloudpickle;
pip install graphviz;
<!-- pip install pyyaml; -->

# to start it back up 
sudo systemctl start airflow-scheduler airflow-ui


