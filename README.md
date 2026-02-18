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