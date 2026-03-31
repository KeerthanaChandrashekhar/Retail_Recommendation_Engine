import pandas as pd
import pickle

# Load model
with open("model.pkl", "rb") as f:
    data = pickle.load(f)

user_item_matrix = data["user_item_matrix"]
user_similarity = data["user_similarity"]

# ------------------------------------------------------------
# LOAD PRODUCT CATALOG (FIXED TYPES)
# ------------------------------------------------------------
df = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")

catalog = (
    df[["StockCode", "Description"]]
    .dropna()
)

# Fix datatype
catalog["StockCode"] = catalog["StockCode"].astype(str)

# 🔥 Keep most frequent description per item
catalog = (
    catalog.groupby("StockCode")["Description"]
    .agg(lambda x: x.mode()[0])   # most common description
    .reset_index()
)

catalog.columns = ["item_id", "description"]

# ------------------------------------------------------------
# RECOMMENDATION FUNCTION
# ------------------------------------------------------------
def recommend_products(user_id, top_n=10):

    if user_id not in user_item_matrix.index:
        print("User not found")
        return None

    # Similar users
    similar_users = user_similarity[user_id].sort_values(ascending=False)[1:6]

    # User purchased items
    user_items = user_item_matrix.loc[user_id]

    # Compute recommendation scores
    recommendations = pd.Series(dtype=float)

    for sim_user, score in similar_users.items():
        sim_items = user_item_matrix.loc[sim_user]
        recommendations = recommendations.add(sim_items * score, fill_value=0)

    # Remove already purchased
    recommendations = recommendations[user_items == 0]

    # Top N
    recommendations = recommendations.sort_values(ascending=False).head(top_n)

    # ------------------------------------------------------------
    # 🔥 CONVERT + FIX TYPE + MERGE
    # ------------------------------------------------------------
    recommendations = recommendations.reset_index()
    recommendations.columns = ["item_id", "score"]

    # 🔥 Match datatype with catalog
    recommendations["item_id"] = recommendations["item_id"].astype(str)

    # Merge with product names
    recommendations = recommendations.merge(catalog, on="item_id", how="left")

    return recommendations


# ------------------------------------------------------------
# TEST
# ------------------------------------------------------------
if __name__ == "__main__":
    sample_user = user_item_matrix.index[0]

    print(f"\nRecommendations for user {sample_user}:\n")

    recs = recommend_products(sample_user)
    print(recs)