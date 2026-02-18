
from werkzeug.security import generate_password_hash
from extensiones import mysql

def crear_admin():
    cur = mysql.connection.cursor()
    password_hash = generate_password_hash("Cual0001$")
    
    cur.execute("""
        INSERT INTO usuarios (username, password, rol)
        VALUES (%s, %s, %s)
    """, ("admin", password_hash, "admin"))
    
    mysql.connection.commit()
    cur.close()
