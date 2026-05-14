from pathlib import Path
import sys
import pandas as pd
from sqlalchemy import create_engine


# Fix Arabic path printing issue on Windows terminal
sys.stdout.reconfigure(encoding="utf-8")


# ==============================
# 1. Project Paths
# ==============================

BASE_PATH = Path(
    r"C:\Users\meana\OneDrive\سطح المكتب\Brazilian E-Commerce Public Dataset by Olist"
)

ANALYTICS_PATH = BASE_PATH / "analytics"
DATABASE_PATH = BASE_PATH / "ecommerce_olist_dw.sqlite"


# ==============================
# 2. Check Analytics Folder
# ==============================

if not ANALYTICS_PATH.exists():
    raise FileNotFoundError(f"Analytics folder not found: {ANALYTICS_PATH}")

print("Analytics path:", ANALYTICS_PATH)


# ==============================
# 3. Create SQLite Engine
# ==============================

engine = create_engine(f"sqlite:///{DATABASE_PATH}")


# ==============================
# 4. Convert Date Columns
# ==============================

def convert_date_columns(df):
    for col in df.columns:
        col_lower = col.lower()

        if "date" in col_lower or "timestamp" in col_lower:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


# ==============================
# 5. Load Analytics Tables
# ==============================

analytics_files = {
    "fact_orders": "fact_orders.csv",
    "fact_order_items": "fact_order_items.csv",
    "monthly_sales": "monthly_sales.csv",
    "customer_analytics": "customer_analytics.csv",
    "product_analytics": "product_analytics.csv",
    "category_analytics": "category_analytics.csv",
    "delivery_performance": "delivery_performance.csv",
    "payment_analytics": "payment_analytics.csv"
}


loaded_count = 0

for table_name, file_name in analytics_files.items():
    file_path = ANALYTICS_PATH / file_name

    if not file_path.exists():
        print(f"Missing file: {file_name}")
        continue

    print(f"\nLoading {file_name} into SQLite table '{table_name}'...")

    df = pd.read_csv(file_path, low_memory=False)
    df = convert_date_columns(df)

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False
    )

    loaded_count += 1
    print(f"Table '{table_name}' loaded successfully. Shape: {df.shape}")


if loaded_count == 0:
    print("\nNo analytics tables were loaded.")
    print("Run 'Analytics Tables.py' first to generate the analytics CSV files.")
else:
    print("\nAll analytics tables loaded into SQLite successfully.")
    print(f"Database file created at: {DATABASE_PATH}")
