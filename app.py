from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import string
import validators
import re
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(20), unique=True, nullable=False)
    clicks = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    expiry = db.Column(db.DateTime)
    password = db.Column(db.String(50))


def generate_code(length=6):
    while True:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if not Link.query.filter_by(short_code=code).first():
            return code


@app.route("/", methods=["GET", "POST"])
def index():
    short_url = None
    if request.method == "POST":

        url = request.form.get("url")
        custom = request.form.get("custom", "").strip().lower()
        if custom == "":
            custom = None

        password = request.form.get("password", "").strip()
        if password == "":
            password = None

        # Validate URL
        if not validators.url(url):
            return render_template("index.html", error="Invalid URL")

        # Validate alias
        if custom:
            if not re.match(r'^[a-zA-Z0-9_-]+$', custom):
                return render_template("index.html", error="Invalid alias format")

            if len(custom) > 20:
                return render_template("index.html", error="Alias too long")

            if Link.query.filter_by(short_code=custom).first():
                return render_template("index.html", error="Alias already exists")

            code = custom
        else:
            code = generate_code()

        existing = Link.query.filter_by(short_code=code).first()
        if existing:
            return render_template(
                "index.html",
                error="Custom alias already exists. Try another."
            )
        expiry_days = request.form.get("expiry", "Never")

        expiry_date = None
        if expiry_days != "Never":
            expiry_date = datetime.utcnow() + timedelta(days=int(expiry_days))

        link = Link(
            original_url=url,
            short_code=code,
            expiry=expiry_date,
            password=password
        )

        db.session.add(link)
        db.session.commit()
        short_url = request.host_url + code

    return render_template("index.html", short_url=short_url)


@app.route("/dashboard")
def dashboard():
  
    links = Link.query.order_by(Link.created.desc()).all()

    total_links = len(links)
    total_clicks = sum(link.clicks for link in links)

    active_links = 0
    protected_links = 0
    expired_links = 0

    for link in links:

        if link.expiry and link.expiry < datetime.utcnow():
            link.status = "Expired"
            expired_links += 1

        elif link.password:
            link.status = "Protected"
            protected_links += 1

        else:
            link.status = "Active"
            active_links += 1

    return render_template(
        "dashboard.html",
        links=links,
        total_links=total_links,
        total_clicks=total_clicks,
        active_links=active_links,
        protected_links=protected_links,
        expired_links=expired_links
    )

@app.route("/<code>", methods=["GET", "POST"])
def redirect_link(code):

    link = Link.query.filter_by(short_code=code).first()

    if not link:
        return "Link not found"

    if link.expiry and datetime.utcnow() > link.expiry:
        return "Link expired"

    if link.password:
        if request.method == "POST":
            if request.form["password"] == link.password:
                link.clicks += 1
                db.session.commit()
                return render_template("preview.html", link=link)
            else:
                return render_template( "password.html", link=link,error="Wrong password. Try again."
    )

        return render_template("password.html")

    link.clicks += 1
    db.session.commit()

    return render_template("preview.html", link=link)


@app.route("/delete/<code>", methods=["POST"])
def delete(code):

    link = Link.query.filter_by(short_code=code).first()

    if link:
        db.session.delete(link)
        db.session.commit()

    return redirect("/dashboard")

@app.route("/check-alias")
def check_alias():

    alias = request.args.get("alias")

    existing = Link.query.filter_by(short_code=alias).first()

    if existing:
        return {"available": False}

    return {"available": True}


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)