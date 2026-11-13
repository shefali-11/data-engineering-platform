
from datetime import datetime
import base64
import urllib.request
from airflow import DAG
from airflow.operators.python import PythonOperator

CLICKHOUSE_URL = "http://medallion-clickhouse:8123/"
AUTH = base64.b64encode(b"default:clickhouse123").decode()

def run_sql(sql):
    request = urllib.request.Request(
        CLICKHOUSE_URL,
        data=sql.encode("utf-8"),
        headers={
            "Authorization": "Basic " + AUTH,
            "Content-Type": "text/plain"
        },
        method="POST"
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode().strip()

def verify_bronze():
    result = run_sql(
        "SELECT count() FROM medallion.bronze_customers"
    )
    print("Bronze rows:", result)

def build_silver():
    run_sql("DROP TABLE IF EXISTS medallion.silver_customers")
    run_sql("""
        CREATE TABLE medallion.silver_customers
        ENGINE = MergeTree
        ORDER BY customer_id
        AS SELECT DISTINCT customer_id, customer_name, city,
        organization_id, processing_date
        FROM medallion.bronze_customers
    """)

def build_gold():
    run_sql("DROP TABLE IF EXISTS medallion.gold_city_summary")
    run_sql("""
        CREATE TABLE medallion.gold_city_summary
        ENGINE = MergeTree
        ORDER BY city
        AS SELECT city, count() AS total_customers
        FROM medallion.silver_customers
        GROUP BY city
    """)

with DAG(
    dag_id="customer_medallion_pipeline",
    start_date=datetime(2026, 10, 1),
    schedule=None,
    catchup=False,
    tags=["clickhouse", "medallion"],
) as dag:
    bronze = PythonOperator(
        task_id="verify_bronze",
        python_callable=verify_bronze,
    )
    silver = PythonOperator(
        task_id="build_silver",
        python_callable=build_silver,
    )
    gold = PythonOperator(
        task_id="build_gold",
        python_callable=build_gold,
    )

    bronze >> silver >> gold
