from pathlib import Path
import sys
import pandas as pd

# Fix Arabic path printing issue on Windows terminal
sys.stdout.reconfigure(encoding="utf-8")

# ==============================
# 1. Dataset Path
# ==============================
DATASET_PATH = Path(
    r"C:\Users\meana\OneDrive\سطح المكتب\Brazilian E-Commerce Public Dataset by Olist\dataSets"
)

print("Dataset path exists:", DATASET_PATH.exists())

# ==============================
# 2. Show All CSV Files
# ==============================
csv_files = list(DATASET_PATH.glob("*.csv"))
print("Number of CSV files:", len(csv_files))

for file in csv_files:
    print(file.name)

# ==============================
# 3. Load All CSV Files Automatically
# ==============================
dataframes = {}

for file in csv_files:
    table_name = file.stem
    dataframes[table_name] = pd.read_csv(file)
    print(f"{table_name} loaded successfully with shape {dataframes[table_name].shape}")

# ==============================
# 4. Create Easy Variable Names
# ==============================
customers = dataframes["olist_customers_dataset"]
orders = dataframes["olist_orders_dataset"]
order_items = dataframes["olist_order_items_dataset"]
products = dataframes["olist_products_dataset"]
payments = dataframes["olist_order_payments_dataset"]
reviews = dataframes["olist_order_reviews_dataset"]
sellers = dataframes["olist_sellers_dataset"]
geolocation = dataframes["olist_geolocation_dataset"]
category_translation = dataframes["product_category_name_translation"]

# ==============================
# 5. Check Dataset Shapes
# ==============================
tables = {
    "customers": customers,
    "orders": orders,
    "order_items": order_items,
    "products": products,
    "payments": payments,
    "reviews": reviews,
    "sellers": sellers,
    "geolocation": geolocation,
    "category_translation": category_translation
}

for name, df in tables.items():
    print(f"{name}: {df.shape[0]} rows, {df.shape[1]} columns")

# ==============================
# 6. Quick Preview of Each Table
# ==============================
for name, df in tables.items():
    print("=" * 80)
    print(name.upper())
    print(df.head())

# ==============================
# 7. Check Missing Values
# ==============================
for name, df in tables.items():
    print("=" * 80)
    print(name.upper())
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if missing.empty:
        print("No missing values")
    else:
        print(missing)

# ==============================
# 8. Check Data Types
# ==============================
for name, df in tables.items():
    print("=" * 80)
    print(name.upper())
    print(df.dtypes)

# ==============================
# 9. Relationship Checks
# ==============================
relationship_checks = {
    "orders.customer_id -> customers.customer_id": (~orders["customer_id"].isin(customers["customer_id"])).sum(),
    "order_items.order_id -> orders.order_id": (~order_items["order_id"].isin(orders["order_id"])).sum(),
    "payments.order_id -> orders.order_id": (~payments["order_id"].isin(orders["order_id"])).sum(),
    "reviews.order_id -> orders.order_id": (~reviews["order_id"].isin(orders["order_id"])).sum(),
    "order_items.product_id -> products.product_id": (~order_items["product_id"].isin(products["product_id"])).sum(),
    "order_items.seller_id -> sellers.seller_id": (~order_items["seller_id"].isin(sellers["seller_id"])).sum()
}

relationship_checks_df = pd.DataFrame(
    relationship_checks.items(),
    columns=["relationship", "missing_records"]
)

print("\nRelationship Checks:")
print(relationship_checks_df)
