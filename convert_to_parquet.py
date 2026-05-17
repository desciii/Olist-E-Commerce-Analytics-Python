import pandas as pd
import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_csv(filename):
    return pd.read_csv(os.path.join(DATA_DIR, filename))


# ══════════════════════════════════════════════════════════════════════════════
# LOAD RAW CSVs
# ══════════════════════════════════════════════════════════════════════════════
print("Loading CSVs...")
orders    = load_csv("olist_orders_dataset.csv")
items     = load_csv("olist_order_items_dataset.csv")
reviews   = load_csv("olist_order_reviews_dataset.csv")
customers = load_csv("olist_customers_dataset.csv")
payments  = load_csv("olist_order_payments_dataset.csv")
products  = load_csv("olist_products_dataset.csv")
category  = load_csv("product_category_name_translation.csv")


# ══════════════════════════════════════════════════════════════════════════════
# CLEAN EACH TABLE BEFORE MERGING
# ══════════════════════════════════════════════════════════════════════════════

print("Cleaning tables...")

# ── orders ────────────────────────────────────────────────────────────────────
# Drop rows with no order_id or customer_id — they're unidentifiable
orders = orders.dropna(subset=["order_id", "customer_id"])

# Remove duplicate order_ids (keep first occurrence)
orders = orders.drop_duplicates(subset="order_id")

# Only keep known valid order statuses — anything else is unidentified noise
VALID_STATUSES = {
    "delivered", "shipped", "canceled", "unavailable",
    "invoiced", "processing", "created", "approved",
}
before = len(orders)
orders = orders[orders["order_status"].isin(VALID_STATUSES)]
print(f"  orders: dropped {before - len(orders)} rows with unknown status")

# Parse all timestamp columns — coerce invalid strings to NaT
DATE_COLS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
for col in DATE_COLS:
    if col in orders.columns:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")

# Drop rows where purchase timestamp is missing — we can't place them on a timeline
before = len(orders)
orders = orders.dropna(subset=["order_purchase_timestamp"])
print(f"  orders: dropped {before - len(orders)} rows with missing purchase timestamp")

# Sanity check: purchase must be before estimated delivery
# (catches corrupted/test rows with inverted dates)
before = len(orders)
has_est = orders["order_estimated_delivery_date"].notna()
bad_dates = has_est & (
    orders["order_purchase_timestamp"] > orders["order_estimated_delivery_date"]
)
orders = orders[~bad_dates]
print(f"  orders: dropped {before - len(orders)} rows with purchase > estimated delivery")

# ── items ─────────────────────────────────────────────────────────────────────
items = items.dropna(subset=["order_id", "product_id"])
items = items.drop_duplicates()

# Negative price or freight is invalid
before = len(items)
items = items[(items["price"] >= 0) & (items["freight_value"] >= 0)]
print(f"  items: dropped {before - len(items)} rows with negative price/freight")

# ── reviews ───────────────────────────────────────────────────────────────────
reviews = reviews.dropna(subset=["order_id", "review_score"])

# Review score must be 1–5 integer
before = len(reviews)
reviews = reviews[reviews["review_score"].between(1, 5)]
print(f"  reviews: dropped {before - len(reviews)} rows with out-of-range review score")

reviews = reviews.drop_duplicates(subset="order_id")

# ── customers ─────────────────────────────────────────────────────────────────
customers = customers.dropna(subset=["customer_id", "customer_unique_id"])
customers = customers.drop_duplicates(subset="customer_id")

# ── payments ──────────────────────────────────────────────────────────────────
payments = payments.dropna(subset=["order_id", "payment_value"])

# Negative payment value is invalid
before = len(payments)
payments = payments[payments["payment_value"] >= 0]
print(f"  payments: dropped {before - len(payments)} rows with negative payment value")

# Installments must be at least 1
payments["payment_installments"] = payments["payment_installments"].clip(lower=1)

# Keep only known payment types
VALID_PAYMENT_TYPES = {"credit_card", "boleto", "voucher", "debit_card", "not_defined"}
before = len(payments)
payments = payments[payments["payment_type"].isin(VALID_PAYMENT_TYPES)]
print(f"  payments: dropped {before - len(payments)} rows with unknown payment type")

payments = payments.drop_duplicates(subset="order_id")

# ── products ──────────────────────────────────────────────────────────────────
products = products.dropna(subset=["product_id"])
products = products.drop_duplicates(subset="product_id")

# ── category translation ──────────────────────────────────────────────────────
category = category.dropna()
category = category.drop_duplicates(subset="product_category_name")


# ══════════════════════════════════════════════════════════════════════════════
# MERGE
# ══════════════════════════════════════════════════════════════════════════════

print("Merging tables...")

df = orders.merge(items, on="order_id", how="left")

df = df.merge(
    reviews[["order_id", "review_score"]],
    on="order_id", how="left",
)

df = df.merge(customers, on="customer_id", how="left")

df = df.merge(
    payments[["order_id", "payment_type", "payment_value", "payment_installments"]],
    on="order_id", how="left",
)

df = df.merge(
    products[["product_id", "product_category_name"]],
    on="product_id", how="left",
)

df = df.merge(category, on="product_category_name", how="left")


# ══════════════════════════════════════════════════════════════════════════════
# POST-MERGE CLEANING
# ══════════════════════════════════════════════════════════════════════════════

print("Post-merge cleaning...")

# ── Derived columns ────────────────────────────────────────────────────────────
df["month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
df["year"]  = df["order_purchase_timestamp"].dt.year

# delivery_days: only meaningful for delivered orders with both dates present
df["delivery_days"] = (
    df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
).dt.days

# Clamp delivery_days — negative means data error, cap outliers at 365 days
before = df["delivery_days"].notna().sum()
df.loc[df["delivery_days"] < 0,   "delivery_days"] = pd.NA
df.loc[df["delivery_days"] > 365, "delivery_days"] = pd.NA
print(f"  delivery_days: nullified {before - df['delivery_days'].notna().sum()} impossible values")

# late: only flag as late when delivered AND both dates are present
delivered_mask = (
    (df["order_status"] == "delivered") &
    df["order_delivered_customer_date"].notna() &
    df["order_estimated_delivery_date"].notna()
)
df["late"] = pd.NA
df.loc[delivered_mask, "late"] = (
    df.loc[delivered_mask, "order_delivered_customer_date"]
    > df.loc[delivered_mask, "order_estimated_delivery_date"]
)

# ── Fill well-known unknowns ───────────────────────────────────────────────────
# product_category_name_english: NaN means no translation exists — label clearly
before = len(df)
df = df.dropna(subset=["product_category_name_english"])
df["product_category_name_english"] = (
    df["product_category_name_english"]
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace(r"\s+", "_", regex=True)
)
df = df[df["product_category_name_english"].str.len() > 0]
print(f"  product_category: dropped {before - len(df)} rows with missing/unidentified category")

# payment_type: NaN after merge means order had no payment record
before = len(df)
df = df.dropna(subset=["payment_type"])
df = df[df["payment_type"].astype(str).str.strip() != ""]
print(f"  payment_type: dropped {before - len(df)} rows with missing/empty payment type")

# review_score: leave as NaN — do NOT impute; charts should handle missing
# customer_state / city: leave as NaN — do NOT impute geography

# ── Remove full duplicates introduced by merge fan-out ─────────────────────────
before = len(df)
df = df.drop_duplicates()
print(f"  post-merge: dropped {before - len(df)} fully duplicate rows")

# ── Final row count sanity check ───────────────────────────────────────────────
print(f"\nFinal dataset: {len(df):,} rows × {len(df.columns)} columns")
print(f"Order statuses present: {sorted(df['order_status'].dropna().unique())}")
print(f"Null counts (top columns):")
null_pct = (df.isnull().mean() * 100).sort_values(ascending=False)
print(null_pct[null_pct > 0].round(1).to_string())


# ══════════════════════════════════════════════════════════════════════════════
# DOWNCAST & SAVE
# ══════════════════════════════════════════════════════════════════════════════

# Downcast numerics to save memory
for col in df.select_dtypes("float64").columns:
    df[col] = df[col].astype("float32")

for col in df.select_dtypes("object").columns:
    if df[col].nunique() < 200:
        df[col] = df[col].astype("category")

df.to_parquet(os.path.join(DATA_DIR, "olist_merged.parquet"), index=False)
print(f"\nSaved! Memory usage: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")