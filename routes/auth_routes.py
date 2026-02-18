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

@auth.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = get_user_by_username(username)

        if user_data and check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1], user_data[3])
            login_user(user)
            return redirect(url_for('user.dashboard'))

        flash("Credenciales incorrectas")

    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
