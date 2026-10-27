
CREATE DATABASE IF NOT EXISTS medallion;

CREATE TABLE IF NOT EXISTS medallion.bronze_customers
(
    customer_id UInt32,
    customer_name String,
    city String,
    organization_id String,
    processing_date Date
)
ENGINE = MergeTree
ORDER BY (organization_id, customer_id);
