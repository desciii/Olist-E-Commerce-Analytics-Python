import pandas as pd
import os

BASE = os.path.join(os.getcwd(), "data")

orders    = pd.read_csv(f"{BASE}/olist_orders_dataset.csv")
items     = pd.read_csv(f"{BASE}/olist_order_items_dataset.csv")
reviews   = pd.read_csv(f"{BASE}/olist_order_reviews_dataset.csv")
customers = pd.read_csv(f"{BASE}/olist_customers_dataset.csv")
payments  = pd.read_csv(f"{BASE}/olist_order_payments_dataset.csv")
products  = pd.read_csv(f"{BASE}/olist_products_dataset.csv")
category  = pd.read_csv(f"{BASE}/product_category_name_translation.csv")

# ── Merge ──────────────────────────────────────────────────────────────────────
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
df = df.merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
df = df.merge(category, on="product_category_name", how="left")

# ── Date parsing ───────────────────────────────────────────────────────────────
df["order_purchase_timestamp"]    = pd.to_datetime(df["order_purchase_timestamp"])
df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])

df["month"]         = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
df["year"]          = df["order_purchase_timestamp"].dt.year
df["delivery_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
df["late"]          = df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]

delivered = df[df["order_status"] == "delivered"].copy()