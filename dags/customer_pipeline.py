from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="customer_data_pipeline",
    start_date=datetime(2026, 10, 4),
    schedule=None,
    catchup=False,
) as dag:

    load_customer_data = BashOperator(
        task_id="load_customer_data",
        bash_command=(
            "cd /opt/airflow && "
            "python scripts/load_to_clickhouse.py"
        ),
    )