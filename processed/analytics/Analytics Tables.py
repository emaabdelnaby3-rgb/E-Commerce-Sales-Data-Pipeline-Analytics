from pathlib import Path
import pandas as pd


# ==============================
# 1. Paths
# ==============================

BASE_PATH = Path(
    r"C:\Users\meana\OneDrive\سطح المكتب\Brazilian E-Commerce Public Dataset by Olist"
)

PROCESSED_PATH = BASE_PATH / "processed"
ANALYTICS_PATH = BASE_PATH / "analytics"

ANALYTICS_PATH.mkdir(exist_ok=True)


# ==============================
# 2. Load Cleaned Data
# ==============================

orders = pd.read_csv(
    PROCESSED_PATH / "orders_cleaned.csv",
    parse_dates=[
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
)

order_items = pd.read_csv(
    PROCESSED_PATH / "order_items_cleaned.csv",
    parse_dates=["shipping_limit_date"]
)

customers = pd.read_csv(PROCESSED_PATH / "customers_cleaned.csv")
products = pd.read_csv(PROCESSED_PATH / "products_cleaned.csv")
payments = pd.read_csv(PROCESSED_PATH / "payments_cleaned.csv")
reviews = pd.read_csv(
    PROCESSED_PATH / "reviews_cleaned.csv",
    parse_dates=["review_creation_date", "review_answer_timestamp"]
)
sellers = pd.read_csv(PROCESSED_PATH / "sellers_cleaned.csv")

print("Cleaned data loaded successfully.")


# ==============================
# 3. Payment Summary
# ==============================
# Important:
# Payments can have multiple records for the same order.
# So we aggregate payments before joining with orders.

payment_summary = payments.groupby("order_id").agg(
    payment_value=("payment_value", "sum"),
    number_of_payment_records=("payment_sequential", "count"),
    max_payment_installments=("payment_installments", "max"),
    payment_types=("payment_type", lambda x: ", ".join(sorted(x.dropna().unique())))
).reset_index()

print("Payment summary created.")


# ==============================
# 4. Order Items Summary
# ==============================

order_items_summary = order_items.groupby("order_id").agg(
    total_items=("order_item_id", "count"),
    total_product_value=("price", "sum"),
    total_freight_value=("freight_value", "sum")
).reset_index()

order_items_summary["order_items_total_value"] = (
    order_items_summary["total_product_value"] +
    order_items_summary["total_freight_value"]
)

print("Order items summary created.")


# ==============================
# 5. Review Summary
# ==============================

review_summary = reviews.groupby("order_id").agg(
    avg_review_score=("review_score", "mean"),
    total_reviews=("review_id", "count")
).reset_index()

print("Review summary created.")


# ==============================
# 6. Fact Orders Table
# ==============================
# One row per order.

fact_orders = orders.merge(
    customers,
    on="customer_id",
    how="left"
)

fact_orders = fact_orders.merge(
    payment_summary,
    on="order_id",
    how="left"
)

fact_orders = fact_orders.merge(
    order_items_summary,
    on="order_id",
    how="left"
)

fact_orders = fact_orders.merge(
    review_summary,
    on="order_id",
    how="left"
)

# Fill missing numeric values
numeric_cols = [
    "payment_value",
    "number_of_payment_records",
    "max_payment_installments",
    "total_items",
    "total_product_value",
    "total_freight_value",
    "order_items_total_value",
    "avg_review_score",
    "total_reviews"
]

for col in numeric_cols:
    fact_orders[col] = fact_orders[col].fillna(0)

fact_orders["payment_types"] = fact_orders["payment_types"].fillna("unknown")

# Extra business columns
fact_orders["order_month_date"] = (
    fact_orders["order_purchase_timestamp"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

fact_orders["is_delivered"] = fact_orders["order_status"].apply(
    lambda x: 1 if x == "delivered" else 0
)

fact_orders["is_cancelled"] = fact_orders["order_status"].apply(
    lambda x: 1 if x == "canceled" else 0
)

print("fact_orders table created.")


# ==============================
# 7. Fact Order Items Table
# ==============================
# One row per product item inside an order.

fact_order_items = order_items.merge(
    orders[
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_year",
            "order_month",
            "order_day",
            "order_weekday",
            "delivery_days",
            "delivery_delay_days",
            "is_delayed"
        ]
    ],
    on="order_id",
    how="left"
)

fact_order_items = fact_order_items.merge(
    customers[
        [
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state"
        ]
    ],
    on="customer_id",
    how="left"
)

fact_order_items = fact_order_items.merge(
    products[
        [
            "product_id",
            "product_category_name",
            "product_category_name_english"
        ]
    ],
    on="product_id",
    how="left"
)

fact_order_items = fact_order_items.merge(
    sellers[
        [
            "seller_id",
            "seller_city",
            "seller_state"
        ]
    ],
    on="seller_id",
    how="left"
)

fact_order_items = fact_order_items.merge(
    review_summary,
    on="order_id",
    how="left"
)

fact_order_items["item_total_value"] = (
    fact_order_items["price"] + fact_order_items["freight_value"]
)

fact_order_items["product_category_name_english"] = (
    fact_order_items["product_category_name_english"].fillna("unknown")
)

fact_order_items["avg_review_score"] = fact_order_items["avg_review_score"].fillna(0)

print("fact_order_items table created.")


# ==============================
# 8. Monthly Sales Table
# ==============================
# We use delivered orders for real sales analysis.

delivered_orders = fact_orders[fact_orders["order_status"] == "delivered"].copy()

monthly_sales = delivered_orders.groupby("order_month_date").agg(
    total_orders=("order_id", "nunique"),
    total_customers=("customer_unique_id", "nunique"),
    total_sales=("payment_value", "sum"),
    avg_order_value=("payment_value", "mean"),
    total_items_sold=("total_items", "sum"),
    delayed_orders=("is_delayed", "sum")
).reset_index()

monthly_sales["delay_rate"] = (
    monthly_sales["delayed_orders"] / monthly_sales["total_orders"]
).round(4)

print("monthly_sales table created.")


# ==============================
# 9. Customer Analytics Table
# ==============================

customer_analytics = delivered_orders.groupby(
    ["customer_unique_id", "customer_city", "customer_state"]
).agg(
    total_orders=("order_id", "nunique"),
    total_spent=("payment_value", "sum"),
    avg_order_value=("payment_value", "mean"),
    first_order_date=("order_purchase_timestamp", "min"),
    last_order_date=("order_purchase_timestamp", "max"),
    avg_delivery_days=("delivery_days", "mean"),
    delayed_orders=("is_delayed", "sum")
).reset_index()

customer_analytics["delay_rate"] = (
    customer_analytics["delayed_orders"] / customer_analytics["total_orders"]
).round(4)

customer_analytics["customer_segment"] = pd.cut(
    customer_analytics["total_spent"],
    bins=[0, 100, 500, 1000, customer_analytics["total_spent"].max()],
    labels=["Low Value", "Medium Value", "High Value", "VIP"],
    include_lowest=True
)

print("customer_analytics table created.")


# ==============================
# 10. Product Analytics Table
# ==============================

delivered_items = fact_order_items[
    fact_order_items["order_status"] == "delivered"
].copy()

product_analytics = delivered_items.groupby(
    ["product_id", "product_category_name_english"]
).agg(
    total_quantity_sold=("order_item_id", "count"),
    total_revenue=("item_total_value", "sum"),
    avg_price=("price", "mean"),
    avg_freight_value=("freight_value", "mean"),
    avg_review_score=("avg_review_score", "mean")
).reset_index()

product_analytics = product_analytics.sort_values(
    by="total_revenue",
    ascending=False
)

print("product_analytics table created.")


# ==============================
# 11. Category Analytics Table
# ==============================

category_analytics = delivered_items.groupby(
    "product_category_name_english"
).agg(
    total_orders=("order_id", "nunique"),
    total_items_sold=("order_item_id", "count"),
    total_revenue=("item_total_value", "sum"),
    avg_price=("price", "mean"),
    avg_freight_value=("freight_value", "mean"),
    avg_review_score=("avg_review_score", "mean")
).reset_index()

category_analytics = category_analytics.sort_values(
    by="total_revenue",
    ascending=False
)

print("category_analytics table created.")


# ==============================
# 12. Delivery Performance Table
# ==============================

delivery_performance = delivered_orders.groupby(
    ["customer_state"]
).agg(
    total_orders=("order_id", "nunique"),
    avg_delivery_days=("delivery_days", "mean"),
    avg_delivery_delay_days=("delivery_delay_days", "mean"),
    delayed_orders=("is_delayed", "sum")
).reset_index()

delivery_performance["delay_rate"] = (
    delivery_performance["delayed_orders"] / delivery_performance["total_orders"]
).round(4)

delivery_performance = delivery_performance.sort_values(
    by="delay_rate",
    ascending=False
)

print("delivery_performance table created.")


# ==============================
# 13. Payment Analytics Table
# ==============================

payments_with_orders = payments.merge(
    orders[["order_id", "order_status"]],
    on="order_id",
    how="left"
)

payments_with_orders = payments_with_orders[
    payments_with_orders["order_status"] == "delivered"
].copy()

payment_analytics = payments_with_orders.groupby("payment_type").agg(
    total_payment_records=("payment_sequential", "count"),
    total_payment_value=("payment_value", "sum"),
    avg_payment_value=("payment_value", "mean"),
    avg_installments=("payment_installments", "mean")
).reset_index()

payment_analytics = payment_analytics.sort_values(
    by="total_payment_value",
    ascending=False
)

print("payment_analytics table created.")


# ==============================
# 14. Save Analytics Tables
# ==============================

fact_orders.to_csv(ANALYTICS_PATH / "fact_orders.csv", index=False)
fact_order_items.to_csv(ANALYTICS_PATH / "fact_order_items.csv", index=False)

monthly_sales.to_csv(ANALYTICS_PATH / "monthly_sales.csv", index=False)
customer_analytics.to_csv(ANALYTICS_PATH / "customer_analytics.csv", index=False)
product_analytics.to_csv(ANALYTICS_PATH / "product_analytics.csv", index=False)
category_analytics.to_csv(ANALYTICS_PATH / "category_analytics.csv", index=False)
delivery_performance.to_csv(ANALYTICS_PATH / "delivery_performance.csv", index=False)
payment_analytics.to_csv(ANALYTICS_PATH / "payment_analytics.csv", index=False)

print("\nAll analytics tables saved successfully.")
print(f"Saved in: {ANALYTICS_PATH}")


# ==============================
# 15. Quick Output Check
# ==============================

analytics_tables = {
    "fact_orders": fact_orders,
    "fact_order_items": fact_order_items,
    "monthly_sales": monthly_sales,
    "customer_analytics": customer_analytics,
    "product_analytics": product_analytics,
    "category_analytics": category_analytics,
    "delivery_performance": delivery_performance,
    "payment_analytics": payment_analytics
}

print("\nAnalytics Tables Summary:")
for name, df in analytics_tables.items():
    print(f"{name}: {df.shape[0]} rows, {df.shape[1]} columns")