from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # للسماح للـ Frontend بالاتصال بـ FastAPI

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
