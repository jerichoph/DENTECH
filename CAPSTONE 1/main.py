from flask import Flask, render_template, request, redirect, url_for, flash, session
import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime, UTC
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"  # required for flash messages

# -----------------------------
# Initialize Firebase safely
# -----------------------------
cred = credentials.Certificate("CAPSTONE 1/dentech_key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

Account_clients = "manual_create_account"


# makita nisa sa diri https://console.cloud.google.com/auth/clients
CLIENT_ID = "921529543911-okjlt4tgb56admos6msdlho9c6ibive8.apps.googleusercontent.com"

# -----------------------------
# 1. LANDING PAGE (Index)
# -----------------------------
@app.route("/", methods=["GET"])
def index():
    name = session.get('name', 'Guest')
    email = session.get('email', '')
    return render_template("index.html", name=name, email=email)

# -----------------------------
# MANUAL LOGIN ROUTE
# -----------------------------

@app.route("/login", methods=["POST"])
def login_manual():
    username = request.form.get("UserName")
    password = request.form.get("Password")

    # Search for user in Firestore
    user_query = db.collection(Account_clients).where("username", "==", username).get()

    if user_query:
        user_data = user_query[0].to_dict()
        # Verify the hashed password
        if check_password_hash(user_data['password'], password):
            session['name'] = user_data['firstname']
            session['email'] = user_data.get('email', '')
            return redirect(url_for("index"))
    
    flash("Invalid username or password!")
    return redirect(url_for("index"))

# -----------------------------
# 2. GOOGLE AUTH ROUTE
# -----------------------------
@app.route("/google-auth", methods=["POST"])
def login_g_auth():
    token = request.form.get("token")
    if not token:
        return render_template("index.html", error="No token provided")

    try:
        # Added clock_skew_in_seconds=10 to handle slight time sync issues
        google_account = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            CLIENT_ID, 
            clock_skew_in_seconds=10
        )
        
        session['uid'] = google_account["sub"]
        session['email'] = google_account["email"]
        session['name'] = google_account.get("name", "User")

        # Save to Firebase
        db.collection("google_create_account").document(session['uid']).set({
            "uid": session['uid'],
            "email": session['email'],
            "name": session['name'],
            "provider": "google",
            "last_login": datetime.now(UTC).isoformat()
        }, merge=True)

        return redirect(url_for("index"))

    except ValueError as e:
        print(f"Token validation failed: {e}")
        flash("Google Login failed. Please try again.")
        return redirect(url_for("index"))

# -----------------------------
# 3. MANUAL SIGN UP
# -----------------------------
@app.route("/sign-up", methods=["POST"])
def sign_up():
    firstname = request.form["FirstName"]
    lastname = request.form["LastName"]
    username = request.form["UserName"]
    password = request.form["Password"]
    mobile = request.form["MobileNumber"]

    check_account = db.collection(Account_clients).where("username", "==", username).get()
    if check_account:
        flash("Username already taken!")
        return redirect(url_for("index"))

    hashed_password = generate_password_hash(password)
    
    db.collection(Account_clients).add({
        "firstname": firstname,
        "lastname": lastname,
        "username": username,
        "password": hashed_password,
        "mobile_number": mobile,
        "created_at": datetime.now(UTC).isoformat()
    })

    session['name'] = firstname
    return redirect(url_for("index"))


# -----------------------------
# 4. LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# -----------------------------
# OTHER ROUTES
# -----------------------------
@app.route("/patient_forms")
def p_forms():
    return render_template("patientForms.html")

@app.route("/about_customer_side")
def about_customer():
    return render_template("aboutcustomer_side.html")

@app.route("/patient-profile")
def p_profile():
    name = session.get('name', 'Guest')
    return render_template("patient-profile.html", name=name)

@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")

if __name__ == "__main__":
    app.run(debug=True)


# pip install google-auth firebase-admin
# pip install flask firebase-admin google-auth
# pip install firebase-admin
# pip install google-auth
# pip install flask