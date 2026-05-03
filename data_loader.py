import pandas as pd
import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

df = pd.read_parquet(os.path.join(DATA_DIR, "olist_merged.parquet"))

delivered = df[df["order_status"] == "delivered"].copy()