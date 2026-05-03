import pandas as pd
import os

# ─────────────────────────────────────────────
# Path setup (works locally + Render)
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_csv(filename):
    return pd.read_csv(os.path.join(DATA_DIR, filename))

# ─────────────────────────────────────────────
# Load datasets
# ─────────────────────────────────────────────
orders    = load_csv("olist_orders_dataset.csv")
items     = load_csv("olist_order_items_dataset.csv")
reviews   = load_csv("olist_order_reviews_dataset.csv")
customers = load_csv("olist_customers_dataset.csv")
payments  = load_csv("olist_order_payments_dataset.csv")
products  = load_csv("olist_products_dataset.csv")
category  = load_csv("product_category_name_translation.csv")

# ─────────────────────────────────────────────
# Merge datasets
# ─────────────────────────────────────────────
df = orders.merge(items, on="order_id", how="left")

df = df.merge(
    reviews[["order_id", "review_score"]].drop_duplicates("order_id"),
    on="order_id", how="left"
)

df = df.merge(customers, on="customer_id", how="left")

df = df.merge(
    payments[["order_id", "payment_type", "payment_value"]].drop_duplicates("order_id"),
    on="order_id", how="left"
)

df = df.merge(
    products[["product_id", "product_category_name"]],
    on="product_id",
    how="left"
)

df = df.merge(category, on="product_category_name", how="left")

df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])

df["month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
df["year"] = df["order_purchase_timestamp"].dt.year
df["delivery_days"] = (
    df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
).dt.days

df["late"] = (
    df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]
)

# dataset used across pages
delivered = df[df["order_status"] == "delivered"].copy()