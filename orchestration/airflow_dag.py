from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG('hightouch_demo_daily',
         start_date=datetime(2025, 8, 1),
         schedule_interval='@daily',
         catchup=False) as dag:

    build = BashOperator(task_id='dbt_build', bash_command='cd warehouse/dbt && dbt build')
    activate = BashOperator(task_id='activate', bash_command='python activation/simulate_reverse_etl.py --segment all --dry-run 1')
    build >> activate
