import os
import pandas as pd
import yaml

BRONZE_DIR = "data/bronze"
SILVER_DIR = "data/silver"
CONFIG_FILE = "configs/silver.yaml"

os.makedirs(SILVER_DIR, exist_ok=True)

# Read YAML configuration
with open(CONFIG_FILE, "r") as file:
    config = yaml.safe_load(file)

tables = config["tables"]

for table_name, table_config in tables.items():

    input_file = os.path.join(BRONZE_DIR, f"{table_name}.csv")
    output_file = os.path.join(SILVER_DIR, f"{table_name}.csv")

    # Read Bronze data
    df = pd.read_csv(input_file)

    # Remove duplicate records
    if table_config.get("deduplicate", False):

        key_columns = table_config["key_columns"]

        before = len(df)

        df = df.drop_duplicates(
            subset=key_columns,
            keep="first"
        )

        after = len(df)

        print(
            f"{table_name}: "
            f"{before} rows -> {after} rows"
        )

    # Save Silver data
    df.to_csv(output_file, index=False)

print()
print("Silver pipeline completed successfully!")