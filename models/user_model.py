from flask_login import UserMixin
from werkzeug.security import check_password_hash
from extensiones import mysql


class User(UserMixin):
    def __init__(self, id, username, rol):
        self.id = id
        self.username = username
        self.rol = rol

def get_user_by_username(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
    data = cur.fetchone()
    cur.close()
    return data

def get_user_by_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    data = cur.fetchone()
    cur.close()
    return data
