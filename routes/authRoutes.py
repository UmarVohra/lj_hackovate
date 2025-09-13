from flask import Blueprint, render_template, redirect, url_for, flash
from extensions import db, bcrypt
from flask_login import login_user, logout_user
from models import User
from forms import RegisterForm, LoginForm

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Account created! You can login now.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
