# ============================================================
# STEP 2: DATA PREPROCESSING (FINAL VERSION)
# ============================================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# ------------------------------------------------------------
# 2.1 LOAD DATASET
# ------------------------------------------------------------
df = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")

print(f"Raw shape: {df.shape}")
print(df.head(3))

# ------------------------------------------------------------
# 2.2 HANDLE MISSING VALUES
# ------------------------------------------------------------
print(f"\nMissing values:\n{df.isnull().sum()}")

df = df.dropna(subset=["Customer ID"]).copy()
df = df.dropna(subset=["Description"]).copy()

df = df[~df["Invoice"].astype(str).str.startswith("C")]
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]

df["Customer ID"] = df["Customer ID"].astype(int)

print(f"\nClean shape: {df.shape}")

# ------------------------------------------------------------
# 2.3 CREATE USER-ITEM INTERACTIONS
# ------------------------------------------------------------
df["purchase_score"] = df["Quantity"] * df["Price"]

interactions = (
    df.groupby(["Customer ID", "StockCode"])["purchase_score"]
    .sum()
    .reset_index()
)

interactions.columns = ["user_id", "item_id", "score"]

# Convert item_id to string (IMPORTANT)
interactions["item_id"] = interactions["item_id"].astype(str)

# Normalize scores
scaler = MinMaxScaler()
interactions["score"] = scaler.fit_transform(interactions[["score"]])

print(f"\nInteractions shape: {interactions.shape}")

# ------------------------------------------------------------
# 2.4 USER-ITEM MATRIX
# ------------------------------------------------------------
user_item_matrix = interactions.pivot_table(
    index="user_id",
    columns="item_id",
    values="score",
    fill_value=0
)

# Ensure column types match
user_item_matrix.columns = user_item_matrix.columns.astype(str)

print(f"\nUser-item matrix shape: {user_item_matrix.shape}")

# ------------------------------------------------------------
# 2.5 SAVE FILES
# ------------------------------------------------------------
interactions.to_csv("interactions.csv", index=False)
user_item_matrix.to_csv("user_item_matrix.csv")

print("✅ Saved interactions.csv & user_item_matrix.csv")

# ------------------------------------------------------------
# 2.6 CREATE PRODUCT CATALOG (FAST VERSION)
# ------------------------------------------------------------
catalog = (
    df[["StockCode", "Description"]]
    .dropna()
)

catalog["StockCode"] = catalog["StockCode"].astype(str)

catalog = (
    catalog.groupby("StockCode")["Description"]
    .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0])
    .reset_index()
)

catalog.columns = ["item_id", "description"]

catalog.to_csv("catalog.csv", index=False)

print("✅ Saved catalog.csv")