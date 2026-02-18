from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from extensiones import mysql

user = Blueprint('user', __name__)

@user.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@user.route('/crear_usuario', methods=['GET','POST'])
@login_required
def crear_usuario():
    if current_user.rol != 'admin':
        flash("No autorizado")
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        rol = request.form['rol']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO usuarios (username,password,rol) VALUES (%s,%s,%s)",
            (username,password,rol)
        )
        mysql.connection.commit()
        cur.close()

        flash("Usuario creado correctamente")

    return render_template('crear_usuario.html')


@user.route('/usuarios')
@login_required
def listar_usuarios():
    if current_user.rol != 'admin':
        return redirect(url_for('user.dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, rol FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()

    return render_template('listar_usuarios.html', usuarios=usuarios)


@user.route('/usuarios/editar/<int:id>', methods=['GET','POST'])
@login_required
def editar_usuario(id):
    if current_user.rol != 'admin':
        return redirect(url_for('user.dashboard'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        username = request.form['username']
        rol = request.form['rol']

        cur.execute("""
            UPDATE usuarios 
            SET username=%s, rol=%s
            WHERE id=%s
        """, (username, rol, id))

        mysql.connection.commit()
        cur.close()
        flash("Usuario actualizado")
        return redirect(url_for('user.listar_usuarios'))

    cur.execute("SELECT id, username, rol FROM usuarios WHERE id=%s", (id,))
    usuario = cur.fetchone()
    cur.close()

    return render_template('editar_usuario.html', usuario=usuario)


@user.route('/usuarios/eliminar/<int:id>')
@login_required
def eliminar_usuario(id):
    if current_user.rol != 'admin':
        return redirect(url_for('user.dashboard'))

    if id == current_user.id:
        flash("No puedes eliminar tu propio usuario")
        return redirect(url_for('user.listar_usuarios'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    flash("Usuario eliminado")
    return redirect(url_for('user.listar_usuarios'))

