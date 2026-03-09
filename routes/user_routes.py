from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

from config import Config
from models.user_model import (
    delete_user,
    get_user_by_id,
    get_user_by_username,
    insert_user,
    list_users,
    update_user,
)
from services.auth_service import is_admin
from services.storage_service import upload_user_image

user = Blueprint("user", __name__)


def _admin_guard():
    if is_admin(current_user):
        return None
    flash("No autorizado")
    return redirect(url_for("user.dashboard"))


@user.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@user.route("/crear_usuario", methods=["GET", "POST"])
@login_required
def crear_usuario():
    """Handle the user creation page.
    On GET, render the user creation form. On POST, validate and process the form data to create a new user.
    """
    guard = _admin_guard()
    if guard:
        return guard

    if request.method == "GET":
        return render_template("crear_usuario.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    rol = request.form.get("rol", "usuario").strip().lower()

    if not username or not password:
        flash("Usuario y contraseña son obligatorios")
        return redirect(url_for("user.crear_usuario"))

    if rol not in {"admin", "usuario"}:
        flash("Rol inválido")
        return redirect(url_for("user.crear_usuario"))

    if get_user_by_username(username):
        flash("El usuario ya existe")
        return redirect(url_for("user.crear_usuario"))

    try:
        photo_key = Config.DEFAULT_USER_IMAGE_KEY
        foto = request.files.get("foto")
        if foto and foto.filename:
            photo_key = upload_user_image(foto, username, foto.filename)

        insert_user(
            username=username,
            password_hash=generate_password_hash(password),
            rol=rol,
            foto_key=photo_key,
        )
        flash("Usuario creado correctamente")
        return redirect(url_for("user.listar_usuarios"))
    except Exception as err:
        flash("No fue posible crear el usuario")
        raise RuntimeError("Error al crear usuario") from err


@user.route("/usuarios")
@login_required
def listar_usuarios():
    """
    Handle the user listing page. Retrieves all users and renders them in a list.
    """
    guard = _admin_guard()
    if guard:
        return guard

    usuarios = list_users()
    return render_template("listar_usuarios.html", usuarios=usuarios)


@user.route("/usuarios/editar/<int:user_id>", methods=["GET", "POST"])
@login_required
def editar_usuario(user_id: int):
    """Handle the user editing page.
    On GET, render the user editing form. On POST, validate and process the form data to update the user.
    """
    guard = _admin_guard()
    if guard:
        return guard

    usuario = get_user_by_id(user_id)
    if not usuario:
        flash("Usuario no encontrado")
        return redirect(url_for("user.listar_usuarios"))

    if request.method == "GET":
        return render_template("editar_usuario.html", usuario=usuario)

    username = request.form.get("username", "").strip()
    rol = request.form.get("rol", "usuario").strip().lower()

    if not username or rol not in {"admin", "usuario"}:
        flash("Datos inválidos")
        return redirect(url_for("user.editar_usuario", user_id=user_id))

    try:
        update_user(user_id, username, rol)
        flash("Usuario actualizado")
        return redirect(url_for("user.listar_usuarios"))
    except Exception as err:
        flash("No fue posible actualizar el usuario")
        raise RuntimeError("Error al actualizar usuario") from err


@user.route("/usuarios/eliminar/<int:user_id>")
@login_required
def eliminar_usuario(user_id: int):
    """
    Handle the user deletion endpoint. Validates permissions and deletes the user if authorized.
    """
    guard = _admin_guard()
    if guard:
        return guard

    if str(user_id) == str(current_user.id):
        flash("No puedes eliminar tu propio usuario")
        return redirect(url_for("user.listar_usuarios"))

    try:
        delete_user(user_id)
        flash("Usuario eliminado")
        return redirect(url_for("user.listar_usuarios"))
    except Exception as err:
        flash("No fue posible eliminar el usuario")
        raise RuntimeError("Error al eliminar usuario") from err
