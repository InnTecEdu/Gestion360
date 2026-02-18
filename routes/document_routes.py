import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from models.document_model import (
    insertar_documento,
    buscar_por_identificador,
    obtener_documento_por_id,
    eliminar_documento_bd,
    actualizar_documento
)



document = Blueprint('document', __name__)

ALLOWED_EXTENSIONS = {'pdf'}


# ✅ Validar extensión
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ✅ Validar identificador
def validar_identificador(identificador):
    return identificador.isdigit() and len(identificador) <= 11


# 🔹 SUBIR DOCUMENTO
@document.route('/subir', methods=['GET', 'POST'])
@login_required
def subir():
    if request.method == 'POST':

        identificador = request.form['identificador']

        # Validar ID
        if not validar_identificador(identificador):
            flash("ID inválido")
            return redirect(request.url)

        # Validar archivo
        if 'file' not in request.files:
            flash("No se seleccionó archivo")
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash("No se seleccionó archivo")
            return redirect(request.url)

        if file and allowed_file(file.filename):

            nombre_original = secure_filename(file.filename)
            nuevo_nombre = str(uuid.uuid4()) + ".pdf"

            # 📂 Crear carpeta por identificador
            carpeta_id = os.path.join(Config.UPLOAD_FOLDER, identificador)

            if not os.path.exists(carpeta_id):
                os.makedirs(carpeta_id)

            # Ruta final
            ruta = os.path.join(carpeta_id, nuevo_nombre)

            # Guardar archivo
            file.save(ruta)

            # Guardar en base de datos
            insertar_documento(
                identificador,
                nombre_original,
                nuevo_nombre,
                ruta,
                current_user.id
            )

            flash("Documento subido correctamente")
            return redirect(url_for('document.subir'))

        else:
            flash("Formato no permitido (solo PDF)")
            return redirect(request.url)

    return render_template('subir.html')


# 🔹 BUSCAR DOCUMENTOS
@document.route('/buscar', methods=['GET', 'POST'])
@login_required
def buscar():

    resultados = []

    if request.method == 'POST':
        identificador = request.form['identificador']

        if validar_identificador(identificador):
            resultados = buscar_por_identificador(identificador)
        else:
            flash("ID inválido")

    return render_template('buscar.html', resultados=resultados)


# 🔹 VER DOCUMENTO
@document.route('/ver/<identificador>/<nombre>')
@login_required
def ver(identificador, nombre):

    ruta = os.path.join(Config.UPLOAD_FOLDER, identificador, nombre)

    if os.path.exists(ruta):
        return send_file(ruta)
    else:
        flash("Archivo no encontrado")
        return redirect(url_for('document.buscar'))
    
@document.route('/eliminar/<int:id_documento>')
@login_required
def eliminar(id_documento):

    doc = obtener_documento_por_id(id_documento)

    if doc:
        ruta = doc['ruta']

        # Eliminar archivo físico
        if os.path.exists(ruta):
            os.remove(ruta)

        # Eliminar registro BD
        eliminar_documento_bd(id_documento)

        flash("Documento eliminado correctamente")

    else:
        flash("Documento no encontrado")

    return redirect(url_for('document.buscar'))

@document.route('/actualizar/<int:id_documento>', methods=['GET', 'POST'])
@login_required
def actualizar(id_documento):

    doc = obtener_documento_por_id(id_documento)

    if not doc:
        flash("Documento no encontrado")
        return redirect(url_for('document.buscar'))

    if request.method == 'POST':

        file = request.files['file']

        if file and allowed_file(file.filename):

            # Eliminar archivo viejo
            if os.path.exists(doc['ruta']):
                os.remove(doc['ruta'])

            nombre_original = secure_filename(file.filename)
            nuevo_nombre = str(uuid.uuid4()) + ".pdf"

            carpeta_id = os.path.join(Config.UPLOAD_FOLDER, doc['identificador'])

            ruta = os.path.join(carpeta_id, nuevo_nombre)

            file.save(ruta)

            actualizar_documento(
                id_documento,
                nombre_original,
                nuevo_nombre,
                ruta
            )

            flash("Documento actualizado correctamente")
            return redirect(url_for('document.buscar'))

    return render_template('actualizar.html', doc=doc)
