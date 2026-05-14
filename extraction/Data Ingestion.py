from pathlib import Path
import pandas as pd

DATASET_PATH = Path(r"C:\Users\meana\OneDrive\سطح المكتب\Brazilian E-Commerce Public Dataset by Olist\dataSets")

print(DATASET_PATH.exists())


csv_files = list(DATASET_PATH.glob("*.csv"))

print("Number of CSV files:", len(csv_files))

for file in csv_files:
    print(file.name)
    
    
    dataframes = {}

for file in csv_files:
    table_name = file.stem
    dataframes[table_name] = pd.read_csv(file)
    print(f"{table_name} loaded successfully with shape {dataframes[table_name].shape}")
    
    
    
    customers = dataframes["olist_customers_dataset"]
orders = dataframes["olist_orders_dataset"]
order_items = dataframes["olist_order_items_dataset"]
products = dataframes["olist_products_dataset"]
payments = dataframes["olist_order_payments_dataset"]
reviews = dataframes["olist_order_reviews_dataset"]
sellers = dataframes["olist_sellers_dataset"]
geolocation = dataframes["olist_geolocation_dataset"]
category_translation = dataframes["product_category_name_translation"]

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
    

for name, df in tables.items():
    print("=" * 80)
    print(name.upper())



summary = []

for name, df in tables.items():
    summary.append({
        "table_name": name,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "duplicate_rows": df.duplicated().sum(),
        "total_missing_values": df.isnull().sum().sum()
    })

summary_df = pd.DataFrame(summary)
summary_df

for name, df in tables.items():
    print("=" * 80)
    print(name.upper())
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    
    if missing.empty:
        print("No missing values")
    else:
        print(missing)
        
for name, df in tables.items():
    print("=" * 80)
    print(name.upper())
    print(df.dtypes)
    print(df.head())
    

print("Orders customers not found in customers table:")
print((~orders["customer_id"].isin(customers["customer_id"])).sum())

print("Order items orders not found in orders table:")
print((~order_items["order_id"].isin(orders["order_id"])).sum())

print("Payments orders not found in orders table:")
print((~payments["order_id"].isin(orders["order_id"])).sum())

print("Reviews orders not found in orders table:")
print((~reviews["order_id"].isin(orders["order_id"])).sum())

print("Order items products not found in products table:")
print((~order_items["product_id"].isin(products["product_id"])).sum())

print("Order items sellers not found in sellers table:")
print((~order_items["seller_id"].isin(sellers["seller_id"])).sum())