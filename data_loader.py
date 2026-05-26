import pandas as pd
import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

df = pd.read_parquet(os.path.join(DATA_DIR, "olist_merged.parquet"))

# Ensure timestamp is datetime (parquet preserves this, but belt-and-suspenders)
df["order_purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"], errors="coerce"
)

# Convenience subset: only fully delivered orders with valid delivery data
delivered = df[
    (df["order_status"] == "delivered") &
    df["order_delivered_customer_date"].notna() &
    df["order_estimated_delivery_date"].notna() &
    df["delivery_days"].notna()
]