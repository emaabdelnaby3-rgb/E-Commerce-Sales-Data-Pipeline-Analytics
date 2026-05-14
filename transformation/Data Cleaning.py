from pathlib import Path
import pandas as pd


# ==============================
# 1. Paths
# ==============================

DATASET_PATH = Path(
    r"C:\Users\meana\OneDrive\سطح المكتب\Brazilian E-Commerce Public Dataset by Olist\dataSets"
)

PROCESSED_PATH = Path(
    r"C:\Users\meana\OneDrive\سطح المكتب\Brazilian E-Commerce Public Dataset by Olist\processed"
)

PROCESSED_PATH.mkdir(exist_ok=True)


# ==============================
# 2. Load Data
# ==============================

customers = pd.read_csv(DATASET_PATH / "olist_customers_dataset.csv")
orders = pd.read_csv(DATASET_PATH / "olist_orders_dataset.csv")
order_items = pd.read_csv(DATASET_PATH / "olist_order_items_dataset.csv")
products = pd.read_csv(DATASET_PATH / "olist_products_dataset.csv")
payments = pd.read_csv(DATASET_PATH / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(DATASET_PATH / "olist_order_reviews_dataset.csv")
sellers = pd.read_csv(DATASET_PATH / "olist_sellers_dataset.csv")
geolocation = pd.read_csv(DATASET_PATH / "olist_geolocation_dataset.csv")
category_translation = pd.read_csv(DATASET_PATH / "product_category_name_translation.csv")


print("Data loaded successfully.")


# ==============================
# 3. Remove Duplicates
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
    before = df.shape[0]
    df.drop_duplicates(inplace=True)
    after = df.shape[0]
    print(f"{name}: removed {before - after} duplicate rows")


# ==============================
# 4. Convert Date Columns
# ==============================

orders_date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for col in orders_date_columns:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")


order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"],
    errors="coerce"
)

reviews["review_creation_date"] = pd.to_datetime(
    reviews["review_creation_date"],
    errors="coerce"
)

reviews["review_answer_timestamp"] = pd.to_datetime(
    reviews["review_answer_timestamp"],
    errors="coerce"
)


print("Date columns converted successfully.")


# ==============================
# 5. Clean Products Table
# ==============================

products["product_category_name"] = products["product_category_name"].fillna("unknown")

numeric_product_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

for col in numeric_product_columns:
    products[col] = products[col].fillna(0)


# Fix spelling mistake in original Olist column names
products.rename(columns={
    "product_name_lenght": "product_name_length",
    "product_description_lenght": "product_description_length"
}, inplace=True)


print("Products table cleaned successfully.")


# ==============================
# 6. Clean Reviews Table
# ==============================

reviews["review_comment_title"] = reviews["review_comment_title"].fillna("No Title")
reviews["review_comment_message"] = reviews["review_comment_message"].fillna("No Comment")

print("Reviews table cleaned successfully.")


# ==============================
# 7. Add English Category Name
# ==============================

products = products.merge(
    category_translation,
    on="product_category_name",
    how="left"
)

products["product_category_name_english"] = products["product_category_name_english"].fillna(
    products["product_category_name"]
)

print("Product category translation added successfully.")


# ==============================
# 8. Create Useful Date Features
# ==============================

orders["order_year"] = orders["order_purchase_timestamp"].dt.year
orders["order_month"] = orders["order_purchase_timestamp"].dt.month
orders["order_day"] = orders["order_purchase_timestamp"].dt.day
orders["order_weekday"] = orders["order_purchase_timestamp"].dt.day_name()

orders["delivery_days"] = (
    orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
).dt.days

orders["estimated_delivery_days"] = (
    orders["order_estimated_delivery_date"] - orders["order_purchase_timestamp"]
).dt.days

orders["delivery_delay_days"] = (
    orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]
).dt.days

orders["is_delayed"] = orders["delivery_delay_days"].apply(
    lambda x: 1 if pd.notnull(x) and x > 0 else 0
)

print("Date features created successfully.")


# ==============================
# 9. Relationship Checks
# ==============================

relationship_checks = {
    "orders.customer_id -> customers.customer_id": (
        ~orders["customer_id"].isin(customers["customer_id"])
    ).sum(),

    "order_items.order_id -> orders.order_id": (
        ~order_items["order_id"].isin(orders["order_id"])
    ).sum(),

    "payments.order_id -> orders.order_id": (
        ~payments["order_id"].isin(orders["order_id"])
    ).sum(),

    "reviews.order_id -> orders.order_id": (
        ~reviews["order_id"].isin(orders["order_id"])
    ).sum(),

    "order_items.product_id -> products.product_id": (
        ~order_items["product_id"].isin(products["product_id"])
    ).sum(),

    "order_items.seller_id -> sellers.seller_id": (
        ~order_items["seller_id"].isin(sellers["seller_id"])
    ).sum()
}

relationship_checks_df = pd.DataFrame(
    relationship_checks.items(),
    columns=["relationship", "missing_records"]
)

print("\nRelationship Checks:")
print(relationship_checks_df)


# ==============================
# 10. Save Cleaned Data
# ==============================

customers.to_csv(PROCESSED_PATH / "customers_cleaned.csv", index=False)
orders.to_csv(PROCESSED_PATH / "orders_cleaned.csv", index=False)
order_items.to_csv(PROCESSED_PATH / "order_items_cleaned.csv", index=False)
products.to_csv(PROCESSED_PATH / "products_cleaned.csv", index=False)
payments.to_csv(PROCESSED_PATH / "payments_cleaned.csv", index=False)
reviews.to_csv(PROCESSED_PATH / "reviews_cleaned.csv", index=False)
sellers.to_csv(PROCESSED_PATH / "sellers_cleaned.csv", index=False)
geolocation.to_csv(PROCESSED_PATH / "geolocation_cleaned.csv", index=False)

relationship_checks_df.to_csv(PROCESSED_PATH / "relationship_checks.csv", index=False)

print("\nAll cleaned files saved successfully in processed folder.")