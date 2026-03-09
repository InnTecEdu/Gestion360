import os
from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models.document_model import (
    delete_document,
    get_document_by_id,
    insert_document,
    search_documents,
    update_document,
)
from services.storage_service import delete_file, get_file_stream, upload_document_file


document = Blueprint("document", __name__)

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validar_identificador(identificador: str) -> bool:
    return identificador.isdigit() and len(identificador) <= 11


@document.route("/subir", methods=["GET", "POST"])
@login_required
def subir():
    """
    Handle the document upload page.
    On GET, render the upload form. On POST, validate and process the uploaded file.
    """
    if request.method == "GET":
        return render_template("subir.html")

    identificador = request.form.get("identificador", "").strip()
    if not validar_identificador(identificador):
        flash("ID inválido")
        return redirect(url_for("document.subir"))

    file = request.files.get("file")
    if not file or not file.filename:
        flash("Debe seleccionar un archivo")
        return redirect(url_for("document.subir"))

    if not allowed_file(file.filename):
        flash("Formato no permitido (solo PDF)")
        return redirect(url_for("document.subir"))

    try:
        nombre_original = secure_filename(file.filename)
        storage_key = upload_document_file(file, identificador, nombre_original)
        nombre_guardado = os.path.basename(storage_key)

        insert_document(
            identificador=identificador,
            nombre_original=nombre_original,
            nombre_guardado=nombre_guardado,
            ruta=storage_key,
            usuario_id=int(current_user.id),
        )

        flash("Documento subido correctamente")
        return redirect(url_for("document.subir"))
    except Exception as err:
        flash("No fue posible subir el documento")
        raise RuntimeError("Error al subir documento") from err


@document.route("/buscar", methods=["GET", "POST"])
@login_required
def buscar():
    """
    Handle the document search page.
    On GET, render the search form. On POST, validate and process the search query.
    """
    resultados = []

    if request.method == "POST":
        termino = request.form.get("identificador", "").strip()
        if not termino:
            flash("Debe ingresar un valor para buscar")
            return render_template("buscar.html", resultados=[])
        resultados = search_documents(termino)

    return render_template("buscar.html", resultados=resultados)


@document.route("/ver/<int:document_id>")
@login_required
def ver(document_id: int):
    """
    Handle the document viewing endpoint. Retrieves the document by ID and serves the file if found.
    """
    doc = get_document_by_id(document_id)
    if not doc:
        flash("Documento no encontrado")
        return redirect(url_for("document.buscar"))

    stream = get_file_stream(doc["ruta"])
    if not stream:
        flash("Archivo no encontrado")
        return redirect(url_for("document.buscar"))

    return send_file(stream, mimetype="application/pdf")


@document.route("/eliminar/<int:id_documento>")
@login_required
def eliminar(id_documento):
    """
    Handle the document deletion endpoint. Validates permissions and deletes the document if authorized.
    """
    doc = get_document_by_id(id_documento)
    if not doc:
        flash("Documento no encontrado")
        return redirect(url_for("document.buscar"))

    if current_user.rol != "admin" and str(doc["usuario_id"]) != str(current_user.id):
        flash("No autorizado para eliminar este documento")
        return redirect(url_for("document.buscar"))

    try:
        delete_file(doc["ruta"])
        delete_document(id_documento)
        flash("Documento eliminado correctamente")
        return redirect(url_for("document.buscar"))
    except Exception as err:
        flash("No fue posible eliminar el documento")
        raise RuntimeError("Error al eliminar documento") from err


@document.route("/actualizar/<int:id_documento>", methods=["GET", "POST"])
@login_required
def actualizar(id_documento):
    """
    Handle the document update page.
    On GET, render the update form. On POST, validate and process the updated file.
    """
    doc = get_document_by_id(id_documento)
    if not doc:
        flash("Documento no encontrado")
        return redirect(url_for("document.buscar"))

    if current_user.rol != "admin" and str(doc["usuario_id"]) != str(current_user.id):
        flash("No autorizado para actualizar este documento")
        return redirect(url_for("document.buscar"))

    if request.method == "GET":
        return render_template("actualizar.html", doc=doc)

    file = request.files.get("file")
    if not file or not file.filename or not allowed_file(file.filename):
        flash("Debe seleccionar un PDF válido")
        return redirect(url_for("document.actualizar", id_documento=id_documento))

    try:
        delete_file(doc["ruta"])
        nombre_original = secure_filename(file.filename)
        storage_key = upload_document_file(file, doc["identificador"], nombre_original)
        nombre_guardado = os.path.basename(storage_key)

        update_document(id_documento, nombre_original, nombre_guardado, storage_key)
        flash("Documento actualizado correctamente")
        return redirect(url_for("document.buscar"))
    except Exception as err:
        flash("No fue posible actualizar el documento")
        raise RuntimeError("Error al actualizar documento") from err
