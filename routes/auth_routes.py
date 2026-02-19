from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from models.user_model import User, get_user_by_username
from extensiones import login_manager

auth = Blueprint('auth', __name__)




@login_manager.user_loader
def load_user(user_id):
    from models.user_model import get_user_by_id
    user = get_user_by_id(user_id)
    if user:
        return User(user[0], user[1], user[3])
    return None

from models.user_model import get_user_by_username, User
from flask_login import login_user


@auth.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Obtener datos del usuario
        user_data = get_user_by_username(username)  # Dict con keys: id, username, password, rol, foto

        if user_data and check_password_hash(user_data['password'], password):
            # Crear el objeto User para flask-login
            user_obj = User(
                id=user_data['id'],
                username=user_data['username'],
                rol=user_data['rol']
            )
            login_user(user_obj)

            # Aquí obtenemos la URL de la foto para usar en la plantilla
            foto_url = url_for('static', filename=f'images/{user_data["foto"]}')

            # Puedes pasarla como parámetro si quieres mostrarla en el dashboard
            return redirect(url_for('user.dashboard'))  # o pasar foto_url en render_template si no rediriges

        else:
            flash("Usuario o contraseña incorrectos")
            return redirect(url_for('auth.login'))

    return render_template('login.html')


# @auth.route('/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         user_data = get_user_by_username(username)  # Esto devuelve un dict gracias a DictCursor

#         if user_data and check_password_hash(user_data['password'], password):
#             # Crear el objeto User con los datos que espera
#             user_obj = User(
#                 id=user_data['id'],
#                 username=user_data['username'],
#                 rol=user_data['rol']
#             )
#             login_user(user_obj)
#             return redirect(url_for('user.dashboard'))

#         else:
#             flash("Usuario o contraseña incorrectos")
#             return redirect(url_for('auth.login'))

#     return render_template('login.html')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
