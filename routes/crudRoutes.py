from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from werkzeug.utils import secure_filename
import os

from extensions import db
from models import Item

items = Blueprint("items", __name__, template_folder="../templates")

UPLOAD_FOLDER = "static/uploads"

@items.route("/", methods=["GET", "POST"])
@login_required
def item_list():
    if request.method == "POST":
        name = request.form.get("name")
        file = request.files.get("image")

        if not name:
            flash("Item name is required", "danger")
            return redirect(url_for("items.item_list"))

        filename = None
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)

        new_item = Item(name=name, image=filename)
        db.session.add(new_item)
        db.session.commit()
        flash("Item added successfully", "success")
        return redirect(url_for("items.item_list"))

    items_data = Item.query.all()
    return render_template("items.html", items=items_data)


@items.route("/update/<int:item_id>", methods=["GET", "POST"])
@login_required
def update_item(item_id):
    item = Item.query.get_or_404(item_id)

    if request.method == "POST":
        name = request.form.get("name")
        file = request.files.get("image")

        if name:
            item.name = name

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)
            item.image = filename

        db.session.commit()
        flash("Item updated successfully", "success")
        return redirect(url_for("items.item_list"))

    return render_template("update_item.html", item=item)


@items.route("/delete/<int:item_id>")
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted successfully", "success")
    return redirect(url_for("items.item_list"))
