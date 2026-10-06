import os
import pandas as pd

# Create output folder
os.makedirs("data", exist_ok=True)

# Organizations
organizations = ["ORG001", "ORG002", "ORG003"]

# Processing dates
processing_dates = [
    "2026-09-28",
    "2026-09-29",
    "2026-09-30",
    "2026-10-01",
    "2026-10-02",
    "2026-10-03",
    "2026-10-04"
]

# Customer data
customers = [
    {"customer_id": 1, "customer_name": "Rahul", "city": "Pune"},
    {"customer_id": 2, "customer_name": "Priya", "city": "Mumbai"},
    {"customer_id": 3, "customer_name": "Amit", "city": "Nagpur"},
    {"customer_id": 4, "customer_name": "Sneha", "city": "Nashik"},
    {"customer_id": 5, "customer_name": "Neha", "city": "Aurangabad"},
]

# Generate data for every organization and date
all_data = []

for organization_id in organizations:
    for processing_date in processing_dates:
        for customer in customers:
            row = customer.copy()
            row["organization_id"] = organization_id
            row["processing_date"] = processing_date
            all_data.append(row)

# Create DataFrame
df = pd.DataFrame(all_data)

# Save as CSV
output_file = "data/customers.csv"
df.to_csv(output_file, index=False)

print("Customer data generated successfully!")
print("Organizations:", len(organizations))
print("Processing dates:", len(processing_dates))
print("Total rows:", len(df))
print()
print(df.head(10))