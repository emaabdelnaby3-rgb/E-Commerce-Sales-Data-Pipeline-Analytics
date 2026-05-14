# E-Commerce Sales Data Pipeline & Analytics

## Project Overview

This project implements an end-to-end **Data Engineering pipeline** for the Brazilian E-Commerce Public Dataset by Olist. The pipeline extracts raw CSV files, performs data cleaning and transformation, creates analytics-ready business tables, loads the final tables into a local SQLite data warehouse, and runs SQL-based business analysis.

The goal of the project is to convert raw e-commerce data into structured, clean, and queryable datasets that can support business insights such as sales trends, product performance, customer segmentation, payment behavior, delivery performance, and order status analysis.

---

## Architecture

![E-Commerce Sales Data Pipeline Architecture](assets/e_commerce_sales_data_pipeline_architecture.png)

---

## Project Workflow

```text
Raw CSV Data
      ↓
Data Ingestion
      ↓
Data Cleaning & Preprocessing
      ↓
Analytics Table Generation
      ↓
SQLite Data Warehouse
      ↓
SQL Business Analysis
```

---

## Dataset

The project uses the **Brazilian E-Commerce Public Dataset by Olist**, which contains multiple relational CSV files representing customers, orders, products, payments, reviews, sellers, geolocation data, and product category translations.

Main dataset files used:

- `olist_customers_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `olist_geolocation_dataset.csv`
- `product_category_name_translation.csv`

---

## Technologies Used

- **Python**
- **Pandas**
- **SQLAlchemy**
- **SQLite**
- **SQL**
- **CSV files**
- **VS Code / Jupyter Notebook**

---

## Project Structure

```text
E-Commerce-Sales-Data-Pipeline-Analytics/
│
├── dataSets/
│   ├── olist_customers_dataset.csv
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   └── product_category_name_translation.csv
│
├── extraction/
│   └── Data Ingestion.py
│
├── transformation/
│   ├── Data Cleaning.py
│   └── Analytics Tables.py
│
├── loading/
│   └── Load To SQLite.py
│
├── sql_analysis/
│   └── Business Analysis Queries.py
│
├── processed/
│   ├── customers_cleaned.csv
│   ├── orders_cleaned.csv
│   ├── order_items_cleaned.csv
│   ├── products_cleaned.csv
│   ├── payments_cleaned.csv
│   ├── reviews_cleaned.csv
│   ├── sellers_cleaned.csv
│   └── geolocation_cleaned.csv
│
├── analytics/
│   ├── fact_orders.csv
│   ├── fact_order_items.csv
│   ├── monthly_sales.csv
│   ├── customer_analytics.csv
│   ├── product_analytics.csv
│   ├── category_analytics.csv
│   ├── delivery_performance.csv
│   └── payment_analytics.csv
│
├── sql_analysis_outputs/
│   ├── monthly_sales_trend.csv
│   ├── top_10_categories_by_revenue.csv
│   ├── top_10_products_by_revenue.csv
│   ├── payment_method_performance.csv
│   ├── delivery_performance_by_state.csv
│   ├── customer_segments.csv
│   └── order_status_distribution.csv
│
├── assets/
│   └── e_commerce_sales_data_pipeline_architecture.png
│
├── ecommerce_olist_dw.sqlite
├── requirements.txt
└── README.md
```

---

## Pipeline Stages

### 1. Data Ingestion

The ingestion stage reads all raw CSV files from the dataset folder using Python and Pandas. It checks the number of files, loads each file into a DataFrame, and performs an initial inspection of rows, columns, missing values, duplicates, and data types.

Main script:

```text
extraction/Data Ingestion.py
```

---

### 2. Data Cleaning

The cleaning stage prepares the raw data for analysis by applying several preprocessing steps:

- Removing duplicate records
- Handling missing values
- Converting date columns to proper datetime format
- Cleaning product and review fields
- Adding English product category names
- Creating useful date-related features
- Validating relationships between tables

Main script:

```text
transformation/Data Cleaning.py
```

Cleaned outputs are saved in:

```text
processed/
```

---

### 3. Analytics Table Generation

This stage creates business-ready analytics tables from the cleaned data. These tables are designed to make analysis easier and faster.

Generated analytics tables include:

- `fact_orders`
- `fact_order_items`
- `monthly_sales`
- `customer_analytics`
- `product_analytics`
- `category_analytics`
- `delivery_performance`
- `payment_analytics`

Main script:

```text
transformation/Analytics Tables.py
```

Analytics outputs are saved in:

```text
analytics/
```

---

### 4. Loading to SQLite Data Warehouse

The analytics-ready tables are loaded into a local SQLite database. SQLite is used as a lightweight local data warehouse because it does not require server installation and is suitable for local data engineering projects.

Main script:

```text
loading/Load To SQLite.py
```

Generated database:

```text
ecommerce_olist_dw.sqlite
```

---

### 5. SQL Business Analysis

After loading the data into SQLite, SQL queries are executed to generate business insights and analysis outputs.

Analysis examples:

- Monthly sales trend
- Top categories by revenue
- Top products by revenue
- Payment method performance
- Delivery performance by customer state
- Customer segmentation
- Order status distribution
- Best and worst reviewed categories

Main script:

```text
sql_analysis/Business Analysis Queries.py
```

Query outputs are saved in:

```text
sql_analysis_outputs/
```

---

## How to Run the Project

### 1. Install Requirements

```bash
pip install -r requirements.txt
```

Or manually install the required libraries:

```bash
pip install pandas sqlalchemy
```

---

### 2. Run the Pipeline Scripts in Order

```bash
python "extraction/Data Ingestion.py"
python "transformation/Data Cleaning.py"
python "transformation/Analytics Tables.py"
python "loading/Load To SQLite.py"
python "sql_analysis/Business Analysis Queries.py"
```

---

## Data Quality Checks

The project performs several validation checks, including:

- Missing values inspection
- Duplicate row detection
- Data type validation
- Date column conversion
- Relationship validation between orders, customers, products, sellers, payments, and reviews

Example relationship checks:

- `orders.customer_id → customers.customer_id`
- `order_items.order_id → orders.order_id`
- `payments.order_id → orders.order_id`
- `reviews.order_id → orders.order_id`
- `order_items.product_id → products.product_id`
- `order_items.seller_id → sellers.seller_id`

---

## Business Analysis Outputs

The SQL analysis stage generates CSV outputs such as:

- `monthly_sales_trend.csv`
- `top_10_categories_by_revenue.csv`
- `top_10_products_by_revenue.csv`
- `payment_method_performance.csv`
- `delivery_performance_by_state.csv`
- `customer_segments.csv`
- `order_status_distribution.csv`
- `best_reviewed_categories.csv`
- `worst_reviewed_categories.csv`

These outputs can be used for reports, presentations, dashboards, or further analysis.

---

## Why SQLite Was Used

SQLite was selected as a lightweight local data warehouse for this project because it is simple to set up, does not require a separate database server, and supports SQL querying. In a production environment, the same pipeline can be migrated to PostgreSQL, MySQL, BigQuery, Snowflake, or another cloud data warehouse.

---

## Key Project Outcomes

By the end of this project, the raw e-commerce dataset is transformed into:

- Cleaned and validated datasets
- Analytics-ready fact and business tables
- A local SQLite data warehouse
- SQL-generated business insights
- A reusable data engineering pipeline

---

## Future Improvements

Possible improvements include:

- Automating the pipeline using Apache Airflow
- Migrating the warehouse from SQLite to PostgreSQL
- Adding dbt for modular SQL transformations
- Building an interactive dashboard using Power BI or Tableau
- Adding data quality tests using Great Expectations
- Dockerizing the full pipeline

---

## Author

**Eman Abdelnaby**

