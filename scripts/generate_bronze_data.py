import os
import pandas as pd

os.makedirs("data/bronze", exist_ok=True)

organizations = ["ORG001", "ORG002", "ORG003"]

processing_dates = [
    "2026-09-28",
    "2026-09-29",
    "2026-09-30",
    "2026-10-01",
    "2026-10-02",
    "2026-10-03",
    "2026-10-04"
]

# 10 Bronze tables
tables = {
    "customers": ["customer_id", "customer_name", "city"],
    "products": ["product_id", "product_name", "category"],
    "orders": ["order_id", "customer_id", "product_id", "quantity"],
    "payments": ["payment_id", "order_id", "amount"],
    "employees": ["employee_id", "employee_name", "department"],
    "departments": ["department_id", "department_name"],
    "suppliers": ["supplier_id", "supplier_name", "city"],
    "inventory": ["inventory_id", "product_id", "quantity"],
    "shipments": ["shipment_id", "order_id", "status"],
    "reviews": ["review_id", "product_id", "rating"]
}

for table_name, columns in tables.items():

    rows = []

    for organization_id in organizations:
        for processing_date in processing_dates:

            for i in range(1, 6):

                row = {}

                for column in columns:

                    if column.endswith("_id"):
                        row[column] = i

                    elif column == "customer_name":
                        row[column] = f"Customer_{i}"

                    elif column == "product_name":
                        row[column] = f"Product_{i}"

                    elif column == "category":
                        row[column] = "Electronics"

                    elif column == "employee_name":
                        row[column] = f"Employee_{i}"

                    elif column == "department_name":
                        row[column] = f"Department_{i}"

                    elif column == "supplier_name":
                        row[column] = f"Supplier_{i}"

                    elif column == "city":
                        row[column] = "Pune"

                    elif column == "quantity":
                        row[column] = i * 10

                    elif column == "amount":
                        row[column] = i * 1000

                    elif column == "rating":
                        row[column] = (i % 5) + 1

                    elif column == "status":
                        row[column] = "Delivered"

                    else:
                        row[column] = i

                row["organization_id"] = organization_id
                row["processing_date"] = processing_date

                rows.append(row)

    df = pd.DataFrame(rows)

    output_file = f"data/bronze/{table_name}.csv"

    df.to_csv(output_file, index=False)

    print(f"Created: {output_file} | Rows: {len(df)}")

print()
print("10 Bronze tables created successfully!")