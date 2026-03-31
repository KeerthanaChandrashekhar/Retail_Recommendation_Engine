# ============================================================
# STEP 2: DATA PREPROCESSING
# Requirements: pip install pandas openpyxl scikit-learn
# ============================================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# ------------------------------------------------------------
# 2.1 LOAD DATASET
# ------------------------------------------------------------
# Update path to where you saved the downloaded file
df = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")

print(f"Raw shape: {df.shape}")
print(df.head(3))
print(df.dtypes)

# ------------------------------------------------------------
# 2.2 HANDLE MISSING VALUES
# ------------------------------------------------------------
print(f"\nMissing values:\n{df.isnull().sum()}")

# Drop rows where CustomerID is missing (can't recommend without a user)
df = df.dropna(subset=["Customer ID"])

# Drop rows where Description is missing (can't label the product)
df = df.dropna(subset=["Description"])

# Remove cancelled orders (InvoiceNo starting with 'C')
df = df[~df["Invoice"].astype(str).str.startswith("C")]

# Remove rows with negative or zero quantity (bad data)
df = df[df["Quantity"] > 0]

# Remove rows with negative or zero price
df = df[df["Price"] > 0]

# Convert CustomerID to integer
df["Customer ID"] = df["Customer ID"].astype(int)

print(f"\nClean shape: {df.shape}")

# ------------------------------------------------------------
# 2.3 CREATE USER-ITEM INTERACTION FORMAT
# ------------------------------------------------------------
# Use: Quantity × UnitPrice as a proxy for "purchase strength"
# This gives higher weight to big/expensive purchases
df["purchase_score"] = df["Quantity"] * df["Price"]

# Aggregate: sum scores per (CustomerID, StockCode) pair
interactions = (
    df.groupby(["Customer ID", "StockCode"])["purchase_score"]
    .sum()
    .reset_index()
)

# Rename columns for clarity
interactions.columns = ["user_id", "item_id", "score"]

# Normalize scores to range [0, 1] for model compatibility
scaler = MinMaxScaler()
interactions["score"] = scaler.fit_transform(interactions[["score"]])

print(f"\nInteractions shape: {interactions.shape}")
print(interactions.head())

# ------------------------------------------------------------
# 2.4 CREATE USER-ITEM MATRIX
# ------------------------------------------------------------
# Rows = users, Columns = products, Values = normalized purchase score
# Missing = 0 (user never bought that product)
user_item_matrix = interactions.pivot_table(
    index="user_id",
    columns="item_id",
    values="score",
    fill_value=0
)

print(f"\nUser-item matrix shape: {user_item_matrix.shape}")
print(f"Sparsity: {(user_item_matrix == 0).sum().sum() / user_item_matrix.size:.2%}")
print(user_item_matrix.iloc[:3, :5])  # Preview

# Save for use in later steps
interactions.to_csv("interactions.csv", index=False)
user_item_matrix.to_csv("user_item_matrix.csv")
print("\n✅ Saved: interactions.csv and user_item_matrix.csv")source venv/Scripts/activate