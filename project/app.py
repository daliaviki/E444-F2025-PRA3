import os
from pathlib import Path
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for,
    abort,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy

# ---------- CONFIG (must be above from_object) ----------
basedir = Path(__file__).resolve().parent
DATABASE = "flaskr.db"
USERNAME = "admin"
PASSWORD = "admin"
SECRET_KEY = "change_me"

# SQLite by default; allow Postgres on Render
url = os.getenv("DATABASE_URL", f"sqlite:///{(basedir / DATABASE)}")
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)
SQLALCHEMY_DATABASE_URI = url
SQLALCHEMY_TRACK_MODIFICATIONS = False

# ---------- APP / DB ----------
app = Flask(__name__)
app.config.from_object(__name__)  # <- loads USERNAME/PASSWORD/SECRET_KEY/etc
db = SQLAlchemy(app)

# import models after db created
from project import models  # noqa: E402


# ---------- HELPERS ----------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in.")
            return jsonify({"status": 0, "message": "Please log in."}), 401
        return f(*args, **kwargs)

    return decorated


# ---------- ROUTES ----------
@app.route("/")
def index():
    entries = db.session.query(models.Post).order_by(models.Post.id.desc()).all()
    return render_template("index.html", entries=entries)


@app.route("/add", methods=["POST"])
def add_entry():
    if not session.get("logged_in"):
        abort(401)
    new_entry = models.Post(request.form["title"], request.form["text"])
    db.session.add(new_entry)
    db.session.commit()
    flash("New entry was successfully posted")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, bounce to home
    if request.method == "GET" and session.get("logged_in"):
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        if request.form.get("username") != app.config["USERNAME"]:
            error = "Invalid username"
        elif request.form.get("password") != app.config["PASSWORD"]:
            error = "Invalid password"
        else:
            session["logged_in"] = True
            flash("You were logged in")
            return redirect(url_for("index"))  # ← CRITICAL
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("You were logged out")
    return redirect(url_for("index"))


@app.route("/delete/<int:post_id>", methods=["GET"])
@login_required
def delete_entry(post_id):
    result = {"status": 0, "message": "Error"}
    try:
        db.session.query(models.Post).filter_by(id=post_id).delete()
        db.session.commit()
        result = {"status": 1, "message": "Post Deleted"}
        flash("The entry was deleted.")
    except Exception as e:
        result = {"status": 0, "message": repr(e)}
    return jsonify(result)


@app.route("/search/", methods=["GET"])
def search():
    query = request.args.get("query", "")
    entries = db.session.query(models.Post).order_by(models.Post.id.desc()).all()
    return render_template("search.html", entries=entries, query=query)


if __name__ == "__main__":
    app.run()
