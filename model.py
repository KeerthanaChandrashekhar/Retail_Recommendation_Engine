import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Load user-item matrix
user_item_matrix = pd.read_csv("user_item_matrix.csv", index_col=0)

# Compute similarity between users
user_similarity = cosine_similarity(user_item_matrix)

# Convert to DataFrame for easy use
user_similarity_df = pd.DataFrame(
    user_similarity,
    index=user_item_matrix.index,
    columns=user_item_matrix.index
)

print("User similarity matrix created")

# Save everything
with open("model.pkl", "wb") as f:
    pickle.dump({
        "user_item_matrix": user_item_matrix,
        "user_similarity": user_similarity_df
    }, f)

print("Model saved successfully")