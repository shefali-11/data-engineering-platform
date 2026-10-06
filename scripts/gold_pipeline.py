import os
import pandas as pd
import yaml

SILVER_DIR = "data/silver"
GOLD_DIR = "data/gold"
CONFIG_FILE = "configs/gold.yaml"

os.makedirs(GOLD_DIR, exist_ok=True)

# Read Gold configuration
with open(CONFIG_FILE, "r") as file:
    config = yaml.safe_load(file)

aggregations = config["aggregations"]

for name, settings in aggregations.items():

    source_table = settings["source_table"]
    source_file = os.path.join(
        SILVER_DIR,
        f"{source_table}.csv"
    )

    df = pd.read_csv(source_file)

    group_by = settings["group_by"]

    result = df.groupby(group_by).size().reset_index(
        name="record_count"
    )

    metrics = settings.get("metrics", {})

    for metric_name, metric_config in metrics.items():

        function = metric_config["function"]
        column = metric_config["column"]

        if function == "count":
            metric = df.groupby(group_by)[column].count().reset_index(
                name=metric_name
            )

        elif function == "sum":
            metric = df.groupby(group_by)[column].sum().reset_index(
                name=metric_name
            )

        else:
            continue

        result = result.drop(columns=["record_count"])
        result = metric

    output_file = os.path.join(
        GOLD_DIR,
        f"{name}.csv"
    )

    result.to_csv(output_file, index=False)

    print(f"Created Gold table: {output_file}")

print()
print("Gold pipeline completed successfully!")