
import os
from pathlib import Path
from datetime import datetime

import boto3
import pandas as pd
import yaml
import pyarrow as pa
import pyarrow.parquet as pq

from airflow import DAG
from airflow.operators.python import PythonOperator


CSV_PATH = "/opt/airflow/dags/extraction/sample.csv"
CONTRACT_PATH = "/opt/airflow/project/schema_contract.yaml"
OUTPUT_DIR = Path("/opt/airflow/datasets/parquet")


def validate_contract():
    with open(CONTRACT_PATH, encoding="utf-8") as file:
        contract = yaml.safe_load(file)

    df = pd.read_csv(CSV_PATH, dtype=str)
    expected = [c["name"] for c in contract["columns"]]

    if list(df.columns) != expected:
        raise ValueError(
            f"Schema mismatch. Expected {expected}, got {list(df.columns)}"
        )

    for column in contract["columns"]:
        name = column["name"]
        kind = column["type"]

        if not column.get("nullable", True):
            if df[name].isna().any() or df[name].str.strip().eq("").any():
                raise ValueError(f"Null or blank value in {name}")

        if kind == "date":
            parsed = pd.to_datetime(
                df[name], format="%Y-%m-%d", errors="coerce"
            )
            if parsed.isna().any():
                raise ValueError(f"Invalid date in {name}")

        elif kind == "integer":
            parsed = pd.to_numeric(df[name], errors="coerce")
            if parsed.isna().any() or (parsed % 1 != 0).any():
                raise ValueError(f"Invalid integer in {name}")

        elif kind == "float":
            parsed = pd.to_numeric(df[name], errors="coerce")
            if parsed.isna().any():
                raise ValueError(f"Invalid number in {name}")

        elif kind != "string" and kind != "date":
            raise ValueError(f"Unsupported type: {kind}")

    print(f"Schema validation passed: {len(df)} rows")


def transform_to_parquet():
    df = pd.read_csv(CSV_PATH, dtype=str)

    for column in df.columns:
        df[column] = df[column].str.strip()

    df["processing_date"] = pd.to_datetime(
        df["processing_date"], format="%Y-%m-%d"
    )

    if OUTPUT_DIR.exists():
        import shutil
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for date_value, group in df.groupby("processing_date"):
        partition = date_value.strftime("%Y-%m-%d")
        folder = OUTPUT_DIR / f"processing_date={partition}"
        folder.mkdir(parents=True, exist_ok=True)

        group = group.copy()
        group["processing_date"] = group["processing_date"].dt.date

        table = pa.Table.from_pandas(group, preserve_index=False)
        pq.write_table(table, folder / "part-00000.parquet")

        print(f"Created Parquet partition: {partition}")


def upload_to_minio():
    client = boto3.client(
        "s3",
        endpoint_url=os.environ["MINIO_ENDPOINT"],
        aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
        aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
        region_name="us-east-1",
    )

    bucket = os.environ["MINIO_BUCKET"]
    files = list(OUTPUT_DIR.rglob("*.parquet"))

    if not files:
        raise ValueError("No Parquet files found")

    for path in files:
        relative = path.relative_to(OUTPUT_DIR).as_posix()
        key = f"customers/{relative}"

        client.upload_file(str(path), bucket, key)
        print(f"Uploaded: {bucket}/{key}")

    print(f"Upload successful: {len(files)} Parquet files")


with DAG(
    dag_id="csv_to_parquet_minio",
    description="Validate CSV and load partitioned Parquet to MinIO",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["stage-2", "minio", "parquet"],
) as dag:

    validate = PythonOperator(
        task_id="validate_contract",
        python_callable=validate_contract,
    )

    transform = PythonOperator(
        task_id="transform_to_parquet",
        python_callable=transform_to_parquet,
    )

    upload = PythonOperator(
        task_id="write_parquet_to_minio",
        python_callable=upload_to_minio,
    )

    validate >> transform >> upload
