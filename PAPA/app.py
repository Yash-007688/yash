from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from authlib.integrations.flask_client import OAuth
import pandas as pd
import os
from user_handler import check_user_credentials, add_new_user, initialize_user_file
from excel_handler import get_excel_data, load_data, save_data, log_edit

app = Flask(__name__)
app.secret_key = "supersecretkey"

# OAuth setup for Google Sign-In
oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    client_kwargs={
        "scope": "openid email profile",
        "prompt": "select_account",
    },
)

# ✅ Ensure Users File Exists
initialize_user_file()


# ✅ Home Route (Redirect to Dashboard or Login)
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ✅ Countdown Page (Before Launch)
@app.route("/countdown")
def countdown():
    return render_template("countdown.html")


# ✅ User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = check_user_credentials(username, password)

        if role:
            session["user"] = username
            session["role"] = role
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="❌ Invalid Credentials")

    return render_template("login.html")


# ✅ User Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        if add_new_user(username, password, role):
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="❌ User already exists!")

    return render_template("register.html")


# ✅ Dashboard (Shows Excel Preview)
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    table_data = get_excel_data()
    return render_template("dashboard.html", user=session["user"], role=session["role"], table=table_data)


# Google OAuth routes
@app.route("/login/google")
def login_google():
    if not oauth.google.client_id or not oauth.google.client_secret:
        return "Google OAuth is not configured on the server.", 500
    redirect_uri = url_for("auth_google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/auth/google/callback")
def auth_google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info_resp = oauth.google.get("userinfo")
        user_info = user_info_resp.json()
        email = user_info.get("email")
        name = user_info.get("name") or email

        if not email:
            return redirect(url_for("login"))

        # Set session for logged-in user; default role as Student
        session["user"] = email
        session["role"] = session.get("role") or "Student"
        return redirect(url_for("dashboard"))
    except Exception as e:
        return f"Google login failed: {str(e)}", 400


# =============================
# Batches (Demo implementation)
# =============================

# Placeholder batches dataset. In a real app, fetch from DB.
BATCHES = [
    {"id": 1, "title": "Mathematics Foundation", "description": "Algebra to Calculus basics", "type": "Free"},
    {"id": 2, "title": "Advanced Physics", "description": "Mechanics, Waves, Optics", "type": "Paid"},
    {"id": 3, "title": "Spoken English", "description": "Daily conversation practice", "type": "Free"},
    {"id": 4, "title": "Data Science Bootcamp", "description": "Python, Pandas, ML", "type": "Paid"},
    {"id": 5, "title": "Chemistry Crash Course", "description": "Organic and Inorganic essentials", "type": "Paid"},
    {"id": 6, "title": "History Essentials", "description": "Ancient to Modern overview", "type": "Free"},
]

# Demo enrollments mapping username -> list of batch IDs
USER_ENROLLMENTS = {
    "Admin": [1, 2, 4],
    "Teacher": [3, 6],
    "Student": [1, 3],
}


@app.route("/batches")
def batches():
    user_logged_in = "user" in session
    username = session.get("user") if user_logged_in else None

    if user_logged_in:
        user_batch_ids = set(USER_ENROLLMENTS.get(username, []))
        my_batches = [b for b in BATCHES if b["id"] in user_batch_ids]
        return render_template(
            "batches.html",
            user_logged_in=True,
            username=username,
            my_batches=my_batches,
        )

    # Not logged in: show all batches vertically with Buy now buttons
    return render_template(
        "batches.html",
        user_logged_in=False,
        all_batches=BATCHES,
    )


# ✅ View & Edit Excel File (For Teachers/Admins)
@app.route("/excel")
def view_excel():
    if "user" not in session:
        return redirect(url_for("login"))

    table_data = get_excel_data()
    return render_template("edit_excel.html", table=table_data)


# ✅ Edit Excel File (Save Changes)
@app.route("/excel/edit", methods=["POST"])
def update_excel():
    if "user" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    try:
        updates = request.form.to_dict(flat=False)
        df = load_data()
        if df is None:
            return jsonify({"success": False, "error": "Excel file not found"})

        for i in range(len(updates["row"])):
            row = int(updates["row"][i])
            col = int(updates["col"][i])
            new_value = updates["value"][i]
            username = session["user"]

            old_value = df.iloc[row, col]
            df.iloc[row, col] = new_value
            log_edit(username, row, col, old_value, new_value)

        save_data(df)

        return jsonify({"success": True, "message": "✅ Excel updated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ✅ View Edit Log (For Admins)
@app.route("/log")
def view_log():
    if "user" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    log_file = "edit_log.xlsx"
    if os.path.exists(log_file):
        log_df = pd.read_excel(log_file, engine="openpyxl")
        logs = log_df.to_dict(orient="records")
        edit_map = {(row["Row"], row["Column"]): row["Username"] for row in logs}
    else:
        logs = []
        edit_map = {}

    table_data = get_excel_data()
    return render_template("view_log.html", logs=logs, table=table_data, edit_map=edit_map)


# ✅ Route to Download Updated Excel File
@app.route("/download")
def download_excel():
    updated_file = "Updated_Patrak.xlsx"
    df = load_data()

    if df is not None:
        df.to_excel(updated_file, index=False, engine="openpyxl")
        return send_file(updated_file, as_attachment=True)

    return "❌ Error: No updated file found.", 404


# ✅ User Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ✅ Run Flask
if __name__ == "__main__":
    app.run(debug=True)
