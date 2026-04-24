import pandas as pd

# Load the CSVs
orders = pd.read_csv("data/olist_orders_dataset.csv")
items = pd.read_csv("data/olist_order_items_dataset.csv")
reviews = pd.read_csv("data/olist_order_reviews_dataset.csv")
customers = pd.read_csv("data/olist_customers_dataset.csv")
payments = pd.read_csv("data/olist_order_payments_dataset.csv")

# Merge into one main dataframe
df = orders.merge(items, on="order_id", how="left")
df = df.merge(reviews[["order_id","review_score"]], on="order_id", how="left")
df = df.merge(customers, on="customer_id", how="left")
df = df.merge(payments[["order_id","payment_type","payment_value"]], on="order_id", how="left")

# Parse dates
df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
df["month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)

print(df.shape)     
print(df.columns)    
print(df.head(3))  