from pathlib import Path
import sys
import pandas as pd
from sqlalchemy import create_engine


# Fix Arabic path printing issue on Windows
sys.stdout.reconfigure(encoding="utf-8")


# ==============================
# 1. Database Path
# ==============================

BASE_PATH = Path(
    r"C:\Users\meana\OneDrive\سطح المكتب\Brazilian E-Commerce Public Dataset by Olist"
)

DATABASE_PATH = BASE_PATH / "ecommerce_olist_dw.sqlite"

OUTPUT_PATH = BASE_PATH / "sql_analysis_outputs"
OUTPUT_PATH.mkdir(exist_ok=True)


# ==============================
# 2. Create SQLite Connection
# ==============================

engine = create_engine(f"sqlite:///{DATABASE_PATH}")

print("Connected to SQLite database successfully.")


# ==============================
# 3. Define Business Queries
# ==============================

queries = {
    "monthly_sales_trend": """
        SELECT
            order_month_date,
            total_orders,
            total_customers,
            ROUND(total_sales, 2) AS total_sales,
            ROUND(avg_order_value, 2) AS avg_order_value,
            total_items_sold,
            delayed_orders,
            delay_rate
        FROM monthly_sales
        ORDER BY order_month_date;
    """,

    "top_10_categories_by_revenue": """
        SELECT
            product_category_name_english,
            total_orders,
            total_items_sold,
            ROUND(total_revenue, 2) AS total_revenue,
            ROUND(avg_price, 2) AS avg_price,
            ROUND(avg_review_score, 2) AS avg_review_score
        FROM category_analytics
        ORDER BY total_revenue DESC
        LIMIT 10;
    """,

    "top_10_products_by_revenue": """
        SELECT
            product_id,
            product_category_name_english,
            total_quantity_sold,
            ROUND(total_revenue, 2) AS total_revenue,
            ROUND(avg_price, 2) AS avg_price,
            ROUND(avg_review_score, 2) AS avg_review_score
        FROM product_analytics
        ORDER BY total_revenue DESC
        LIMIT 10;
    """,

    "payment_method_performance": """
        SELECT
            payment_type,
            total_payment_records,
            ROUND(total_payment_value, 2) AS total_payment_value,
            ROUND(avg_payment_value, 2) AS avg_payment_value,
            ROUND(avg_installments, 2) AS avg_installments
        FROM payment_analytics
        ORDER BY total_payment_value DESC;
    """,

    "delivery_performance_by_state": """
        SELECT
            customer_state,
            total_orders,
            ROUND(avg_delivery_days, 2) AS avg_delivery_days,
            ROUND(avg_delivery_delay_days, 2) AS avg_delivery_delay_days,
            delayed_orders,
            delay_rate
        FROM delivery_performance
        ORDER BY delay_rate DESC;
    """,

    "customer_segments": """
        SELECT
            customer_segment,
            COUNT(*) AS number_of_customers,
            ROUND(SUM(total_spent), 2) AS total_segment_revenue,
            ROUND(AVG(total_spent), 2) AS avg_customer_spending,
            ROUND(AVG(total_orders), 2) AS avg_orders_per_customer
        FROM customer_analytics
        GROUP BY customer_segment
        ORDER BY total_segment_revenue DESC;
    """,

    "order_status_distribution": """
        SELECT
            order_status,
            COUNT(*) AS total_orders,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_orders), 2) AS percentage
        FROM fact_orders
        GROUP BY order_status
        ORDER BY total_orders DESC;
    """,

    "top_10_customer_states_by_sales": """
        SELECT
            customer_state,
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(DISTINCT customer_unique_id) AS total_customers,
            ROUND(SUM(payment_value), 2) AS total_sales,
            ROUND(AVG(payment_value), 2) AS avg_order_value
        FROM fact_orders
        WHERE order_status = 'delivered'
        GROUP BY customer_state
        ORDER BY total_sales DESC
        LIMIT 10;
    """,

    "best_reviewed_categories": """
        SELECT
            product_category_name_english,
            total_items_sold,
            ROUND(total_revenue, 2) AS total_revenue,
            ROUND(avg_review_score, 2) AS avg_review_score
        FROM category_analytics
        WHERE total_items_sold >= 100
        ORDER BY avg_review_score DESC
        LIMIT 10;
    """,

    "worst_reviewed_categories": """
        SELECT
            product_category_name_english,
            total_items_sold,
            ROUND(total_revenue, 2) AS total_revenue,
            ROUND(avg_review_score, 2) AS avg_review_score
        FROM category_analytics
        WHERE total_items_sold >= 100
        ORDER BY avg_review_score ASC
        LIMIT 10;
    """
}


# ==============================
# 4. Run Queries and Save Results
# ==============================

for query_name, query in queries.items():
    print("\n" + "=" * 80)
    print(query_name.upper())
    print("=" * 80)

    result = pd.read_sql(query, engine)

    print(result.head(10))

    output_file = OUTPUT_PATH / f"{query_name}.csv"
    result.to_csv(output_file, index=False)

    print(f"Saved: {output_file.name}")


print("\nAll SQL analysis queries executed successfully.")
print("Results saved in sql_analysis_outputs folder.")