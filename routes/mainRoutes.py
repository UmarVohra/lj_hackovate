from flask import Blueprint, render_template
from flask_login import login_required
from models import Item

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("base.html")

@main.route("/dashboard")
@login_required
def dashboard():
    items = Item.query.all()
    return render_template("dashboard.html", items=items)
