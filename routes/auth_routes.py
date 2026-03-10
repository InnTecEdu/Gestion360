from __future__ import annotations

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
    flash,
)
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash

from infrastructure import login_manager
from models.user_model import get_user_by_id, get_user_by_username
from services.auth_service import build_login_user
from services.storage_service import get_file_stream

auth = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id: str):
    user_data = get_user_by_id(user_id)
    if not user_data:
        return None
    return build_login_user(user_data)


@auth.route("/", methods=["GET", "POST"])
def login():
    """
    Manaje the login page and authentication process.
    On GET, render the login form. On POST, validate credentials and log in the user.
    """
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        flash("Debe completar usuario y contraseña")
        return redirect(url_for("auth.login"))

    try:
        user_data = get_user_by_username(username)
        valid_credentials = bool(
            user_data and check_password_hash(user_data["password"], password)
        )

        if not valid_credentials:
            flash("Usuario o contraseña incorrectos")
            return redirect(url_for("auth.login"))

        if user_data is None:
            flash("Usuario o contraseña incorrectos")
            return redirect(url_for("auth.login"))

        login_user(build_login_user(user_data))
        return redirect(url_for("user.dashboard"))
    except Exception as err:
        flash("No fue posible iniciar sesión")
        raise RuntimeError("Error al autenticar usuario") from err


@auth.route("/get_user_photo/<username>")
def get_user_photo(username: str):
    """
    Endpoint to retrieve the URL of a user's profile photo. If the user has no photo, returns the URL of a default image.
    """
    user_data = get_user_by_username(username)
    if not user_data:
        return jsonify({"foto": url_for("static", filename="images/default-user.jpg")})

    photo_key = (user_data.get("foto") or "").strip()
    if not photo_key:
        return jsonify({"foto": url_for("static", filename="images/default-user.jpg")})

    if photo_key.startswith("static/"):
        return jsonify(
            {"foto": url_for("static", filename=photo_key.replace("static/", "", 1))}
        )

    return jsonify({"foto": url_for("auth.user_photo", user_id=user_data["id"])})


@auth.route("/user_photo/<int:user_id>")
def user_photo(user_id: int):
    """
    Endpoint to serve the user's profile photo. If the user has no photo or if there's an error retrieving it, serves a default image.
    """
    user_data = get_user_by_id(user_id)
    if not user_data:
        return redirect(url_for("static", filename="images/default-user.jpg"))

    photo_key = (user_data.get("foto") or "").strip()
    if not photo_key:
        return redirect(url_for("static", filename="images/default-user.jpg"))

    if photo_key.startswith("static/"):
        return redirect(url_for("static", filename=photo_key.replace("static/", "", 1)))

    stream = get_file_stream(photo_key)
    if not stream:
        return redirect(url_for("static", filename="images/default-user.jpg"))

    return send_file(stream, mimetype="image/jpeg")


@auth.route("/logout")
def logout():
    """Log out the current user and redirect to the login page.
    """
    logout_user()
    return redirect(url_for("auth.login"))
