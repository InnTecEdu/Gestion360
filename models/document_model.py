from extensiones import mysql
import MySQLdb.cursors


def insertar_documento(identificador, nombre_original, nombre_guardado, ruta, usuario_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO documentos 
        (identificador, nombre_original, nombre_guardado, ruta, usuario_id)
        VALUES (%s,%s,%s,%s,%s)
    """, (identificador, nombre_original, nombre_guardado, ruta, usuario_id))
    mysql.connection.commit()
    cur.close()


def buscar_documentos(termino):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 🔎 Buscar por identificador exacto o nombre parcial
    cur.execute("""
        SELECT * FROM documentos 
        WHERE identificador = %s
        OR nombre_completo LIKE %s
    """, (termino, f"%{termino}%"))

    data = cur.fetchall()
    cur.close()
    return data

def obtener_documento_por_id(id_documento):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM documentos WHERE id = %s", (id_documento,))
    data = cur.fetchone()
    cur.close()
    return data


def eliminar_documento_bd(id_documento):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM documentos WHERE id = %s", (id_documento,))
    mysql.connection.commit()
    cur.close()



def actualizar_documento(id_documento, nombre_original, nombre_guardado, ruta):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE documentos
        SET nombre_original=%s,
            nombre_guardado=%s,
            ruta=%s
        WHERE id=%s
    """, (nombre_original, nombre_guardado, ruta, id_documento))
    mysql.connection.commit()
    cur.close()
