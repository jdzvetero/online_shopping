from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="../templates/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("shop.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "customer")
        brand_name = request.form.get("brand_name", "").strip()

        error = None
        if not name or not email or not password:
            error = "Please fill in all required fields."
        elif role not in ("customer", "seller"):
            error = "Please choose a valid account type."
        elif role == "seller" and not brand_name:
            error = "Please tell us your brand name."
        elif User.query.filter_by(email=email).first():
            error = "An account with this email already exists."

        if error:
            flash(error, "error")
            return render_template("auth/register.html", form=request.form)

        user = User(name=name, email=email, role=role, brand_name=brand_name or None)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Welcome to Veloura, {user.name.split(' ')[0]}!", "success")
        if user.is_seller:
            return redirect(url_for("seller.dashboard"))
        return redirect(url_for("shop.index"))

    return render_template("auth/register.html", form={})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("shop.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        next_url = request.form.get("next")

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash("Incorrect email or password.", "error")
            return render_template("auth/login.html", email=email)

        login_user(user)
        flash(f"Welcome back, {user.name.split(' ')[0]}!", "success")
        if next_url:
            return redirect(next_url)
        if user.is_seller:
            return redirect(url_for("seller.dashboard"))
        return redirect(url_for("shop.index"))

    return render_template("auth/login.html", email="")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("shop.index"))
