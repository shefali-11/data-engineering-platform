import pandas as pd
import clickhouse_connect

# Read CSV
df = pd.read_csv("data/customers.csv")

# Convert date
df["processing_date"] = pd.to_datetime(df["processing_date"]).dt.date

# Connect to ClickHouse
client = clickhouse_connect.get_client(
    host="clickhouse",
    port=8123,
    username="default",
    password="clickhouse123",
    database="data_engineering"
)

# Create table
client.command("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id UInt32,
    customer_name String,
    city String,
    organization_id String,
    processing_date Date
)
ENGINE = MergeTree()
ORDER BY (organization_id, processing_date, customer_id)
""")

# Insert data
client.insert_df("customers", df)

print("Data loaded successfully!")
print("Rows loaded:", len(df))