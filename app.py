from flask_cors import CORS
from flask import Flask, jsonify, request, send_from_directory
import pickle
from recommend import recommend_products

app = Flask(__name__)
CORS(app)

# Load model
with open("model.pkl", "rb") as f:
    data = pickle.load(f)

user_item_matrix = data["user_item_matrix"]

# ------------------------------------------------------------
# HOME
# ------------------------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "Retail Recommendation API running",
        "use": "/recommend/<user_id>"
    })

# ------------------------------------------------------------
# SERVE UI
# ------------------------------------------------------------
@app.route("/ui")
def serve_ui():
    return send_from_directory(".", "index.html")

# ------------------------------------------------------------
# RECOMMEND API
# ------------------------------------------------------------
@app.route("/recommend/<int:user_id>")
def recommend(user_id):
    try:
        n = int(request.args.get("n", 10))

        if user_id not in user_item_matrix.index:
            return jsonify({"error": "User not found"}), 404

        recs = recommend_products(user_id, top_n=n)

        return jsonify({
            "user_id": user_id,
            "count": len(recs),
            "recommendations": recs.to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users")
def get_users():
    sample_users = list(user_item_matrix.index[:10])
    return jsonify({
        "sample_ids": sample_users
    })
# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)