from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# Initialize Firebase safely
# -----------------------------
cred = credentials.Certificate("dentech_key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

Account_clients= "manual_create_account"



@app.route("/sign_up_google")
def index():
    return render_template("index.html")

#makita nisa sa diri https://console.cloud.google.com/auth/clients?orgonly=true&project=dentech-c2ee0&supportedpurview=organizationId

CLIENT_ID = "921529543911-okjlt4tgb56admos6msdlho9c6ibive8.apps.googleusercontent.com"



@app.route("/google-auth", methods=["POST"])
def login_g_auth():
    token = request.form["token"]

    try:
        google_account = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            CLIENT_ID
        )

        uid = google_account["sub"]
        email = google_account["email"]
        name = google_account.get("name", "")

        # Save to Firebase
        db.collection("google_create_account").document(uid).set({
            "uid": uid,
            "email": email,
            "name": name,
            "provider": "google",
            "created_at": datetime.utcnow().isoformat()
        }, merge=True)

        return render_template("index.html", email=email, name=name)

    except ValueError:
        return render_template("error.html", message="Invalid Google token")





@app.route("/prac_sign_up")
def prac_google_auth():
    return render_template("sign_up.html")

@app.route("/", methods=["GET", "POST"])
def create_account_page():
    if request.method == "POST":
        firstname = request.form["FirstName"]
        lastname = request.form["LastName"]
        mobile_number = request.form["MobileNumber"]
        username = request.form["UserName"]
        password = request.form["Password"]

        # 🔹 Check if username already exists
        exist_account = db.collection(Account_clients)
        check_account = exist_account.where("username", "==", username).get()

        if check_account:
            Flask("May naka-register na nga account sa sini nga username!")
            return redirect(url_for("create_account_page"))

        # Add new user 
        exist_account.add({
            "firstname": firstname,
            "lastname": lastname,
            "mobile_number": mobile_number,
            "username": username,
            "password": password, 
            "created_at": datetime.utcnow().isoformat()
        })

        return redirect(url_for("about_customer"))

    return render_template("sign_up_customer.html")


@app.route("/patient_forms")
def p_forms():
    return render_template("patientForms.html")


@app.route("/about_customer_side")
def about_customer():
    return render_template("aboutcustomer_side.html")



if __name__ == "__main__":
    app.run(debug=True)


#pip install google-auth firebase-admin
#pip install flask firebase-admin google-auth
#pip install firebase-admin
#pip install google-auth
#pip install flask


