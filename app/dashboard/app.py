from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from flask import jsonify

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your_secret_key"  

API_BASE_URL = "http://127.0.0.1:8000/api"

# ---------- LOGIN & AUTH ----------
@app.route("/")
def home():
    if "token" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        response = requests.post(f"{API_BASE_URL}/users/login", data={"username": email, "password": password})
        if response.status_code == 200:
            data = response.json()
            session["token"] = data["access_token"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password!", "danger")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("token", None)
    return redirect(url_for("login"))

# ---------- DASHBOARD & CRUD OPERATIONS ----------
@app.route("/dashboard")
def dashboard():
    if "token" not in session:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {session['token']}"}

    try:
        response = requests.get(f"{API_BASE_URL}/courses", headers=headers)

        # Debugging API response
        print(f"📡 API Response: {response.status_code}, {response.text}")

        if response.status_code == 200:
            courses = response.json()
        else:
            flash(f"⚠️ Error fetching courses: {response.status_code}", "danger")
            courses = []  # Ensure courses is always a list

    except requests.exceptions.ConnectionError:
        flash("⚠️ Could not connect to the API server.", "danger")
        courses = []

    return render_template("dashboard.html", courses=courses)






@app.route("/add_course", methods=["POST"])
def add_course():
    if "token" not in session:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {session['token']}"}
    course_data = {
        "name": request.form["name"],
        "level": request.form["level"],
        "description": request.form["description"],
        "category": request.form["category"],
        "language": request.form["language"],
        "image_url": request.form["image_url"],
        "status": "active"
    }

    response = requests.post(f"{API_BASE_URL}/courses/", json=course_data, headers=headers)

    if response.status_code == 200:
        flash("Course added successfully!", "success")
    else:
        flash("Failed to add course! Check your permissions.", "danger")

    return redirect(url_for("dashboard"))

@app.route("/delete_course/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    if "token" not in session:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {session['token']}"}
    response = requests.delete(f"{API_BASE_URL}/courses/{course_id}", headers=headers)

    if response.status_code == 200:
        flash("Course deleted successfully!", "success")
    else:
        flash("Failed to delete course! Check your permissions.", "danger")

    return redirect(url_for("dashboard"))



@app.route("/update_course/<int:course_id>", methods=["POST"])
def update_course(course_id):
    if "token" not in session:
        return redirect(url_for("login"))

    updated_data = {
        "name": request.form.get("name"),
        "level": request.form.get("level"),
        "description": request.form.get("description"),
        "category": request.form.get("category"),
        "language": request.form.get("language"),
        "image_url": request.form.get("image_url"),
        "status": request.form.get("status")
    }

    headers = {"Authorization": f"Bearer {session['token']}", "Content-Type": "application/json"}
    response = requests.put(f"{API_BASE_URL}/courses/{course_id}", json=updated_data, headers=headers)

    if response.status_code == 200:
        flash("✅ Course updated successfully!", "success")
    else:
        flash(f"❌ Failed to update course! {response.text}", "danger")

    return redirect(url_for("dashboard"))





if __name__ == "__main__":
    app.run(debug=True, port=5000)
