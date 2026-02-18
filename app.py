import os
from flask import Flask
from config import Config
from extensiones import mysql, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from routes.auth_routes import auth
    from routes.user_routes import user
    from routes.document_routes import document

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(document)

    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
