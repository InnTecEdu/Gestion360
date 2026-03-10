from os import path, makedirs

from flask import Flask, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import inspect

from config import Config
from infrastructure import db, init_infrastructure
from routes.auth_routes import auth
from routes.document_routes import document
from routes.user_routes import user


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_infrastructure(app)

    with app.app_context():
        from models import entities  # noqa: F401

        _create_missing_tables(app)

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(document)

    _ensure_local_directories(app)
    _register_error_handlers(app)

    return app


def _ensure_local_directories(app: Flask) -> None:
    upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
    if not path.exists(upload_folder):
        makedirs(upload_folder)


def _create_missing_tables(app: Flask) -> None:
    if not app.config.get("DB_AUTO_CREATE", False):
        app.logger.info(
            "DB_AUTO_CREATE deshabilitado: no se crean tablas automáticamente"
        )
        return

    inspector = inspect(db.engine)
    existing = set(inspector.get_table_names())
    missing_tables = [
        table for name, table in db.metadata.tables.items() if name not in existing
    ]

    if not missing_tables:
        app.logger.info("No hay tablas faltantes para crear")
        return

    db.metadata.create_all(bind=db.engine, tables=missing_tables)
    created_names = ", ".join(table.name for table in missing_tables)
    app.logger.info("Tablas creadas por ORM: %s", created_names)


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_err):
        return render_template("base.html"), 404

    @app.errorhandler(413)
    def file_too_large(_err):
        flash("El archivo excede el tamaño máximo permitido")
        return redirect(url_for("document.subir"))

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        app.logger.exception("Error no controlado: %s", err)
        flash("Se produjo un error inesperado")
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        return redirect(url_for("user.dashboard"))


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
