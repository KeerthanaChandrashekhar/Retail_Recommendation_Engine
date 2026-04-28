from flask_cors import CORS
from flask import Flask, jsonify, request, send_from_directory
import pickle
from recommend import recommend_products
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

app = Flask(__name__, static_folder='.')
CORS(app)

# Load model
with open("model.pkl", "rb") as f:
    data = pickle.load(f)

user_item_matrix = data["user_item_matrix"]

# ------------------------------------------------------------
# EMAIL CONFIG
# ------------------------------------------------------------
SENDER_EMAIL = "keerthana2043@gmail.com"
APP_PASSWORD = "dzam hrjh rfeb okku"

users_df = pd.read_csv("users.csv")

# Create mapping
user_email_map = dict(zip(
    users_df["user_id"].astype(str),
    users_df["email"]
))


def format_message(products):

    lines = [
        "Hi 👋",
        "",
        "Based on your recent purchases, we think you'll love these:",
        ""
    ]

    for p in products:
        name = p.get("description", "Product")
        lines.append(f"• {name}")

    lines += [
        "",
        "Explore more products in our store!",
        "",
        "— shopAI Recommendations"
    ]

    return "\n".join(lines)


def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

        return True, None

    except Exception as e:
        return False, str(e)

# ------------------------------------------------------------
# HOME
# ------------------------------------------------------------
@app.route("/")
def home():
    return send_from_directory(".", "login.html")

# ------------------------------------------------------------
# SERVE UI
# ------------------------------------------------------------
@app.route("/ui")
def serve_ui():
    return send_from_directory(".", "index.html")

@app.route("/index.html")
def serve_index():
    return send_from_directory(".", "index.html")


@app.route("/dashboard.html")
def serve_dashboard():
    return send_from_directory(".", "dashboard.html")


@app.route("/product.html")
def serve_product():
    return send_from_directory(".", "product.html")

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
# SEND EMAIL RECOMMENDATIONS
# ------------------------------------------------------------
@app.route("/send_recommendations/<int:user_id>")
def send_recommendations(user_id):

    email = user_email_map.get(str(user_id), "default@gmail.com")
    if not email:
        return jsonify({"error": "No email found"}), 404

    try:
        recs = recommend_products(user_id, top_n=10)

        products = recs.head(5).to_dict(orient="records")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    body = format_message(products)
    subject = "Recommended for You"

    success, err = send_email(email, subject, body)

    if success:
        return jsonify({
            "status": "Email sent successfully",
            "sent_to": email,
            "user_id": user_id,
            "num_products": len(products)
        })
    else:
        return jsonify({"error": err}), 500
    
 
@app.route("/send_recommendations_all")
def send_recommendations_all():
    results = []

    for user_id_str, email in user_email_map.items():
        try:
            user_id = int(user_id_str)

            recs = recommend_products(user_id, top_n=10)

            if recs is None:
                continue

            if hasattr(recs, "head"):
                products = recs.head(5).to_dict(orient="records")
            else:
                products = recs[:5]

            body = format_message(products)

            success, err = send_email(email, "Recommended for You", body)

            results.append({
                "user": user_id,
                "status": "sent" if success else "failed"
            })

        except Exception as e:
            results.append({
                "user": user_id,
                "status": "error"
            })

    return {
        "status": "done",
        "total": len(results)
    }

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)