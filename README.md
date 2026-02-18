pip install flask flask-mysqldb flask-login werkzeug

archivo_digital/
│
├── app.py
├── config.py
├── requirements.txt
│
├── /models
│     ├── __init__.py
│     ├── user_model.py
│     └── document_model.py
│
├── /routes
│     ├── __init__.py
│     ├── auth_routes.py
│     ├── user_routes.py
│     └── document_routes.py
│
├── /templates
│     ├── login.html
│     ├── dashboard.html
│     ├── crear_usuario.html
│     ├── subir.html
│     ├── buscar.html
│
├── /uploads





Pasos instalación

virtualenv env
source env/Scripts/activate
pip install -r requirements.txt
py app.py

Crear BD
archivo_digital


CREATE TABLE documentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    identificador VARCHAR(100) NOT NULL,
    nombre_original VARCHAR(255) NOT NULL,
    nombre_guardado VARCHAR(255) NOT NULL,
    ruta VARCHAR(500) NOT NULL,
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (identificador),
    INDEX (usuario_id),
    
    CONSTRAINT fk_documentos_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
);


CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


