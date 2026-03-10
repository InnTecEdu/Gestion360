from os import getenv
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Import dotenv variables before defining Config to ensure they are available when Config is initialized
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = getenv("SECRET_KEY", "change-me-in-production")
    UPLOAD_FOLDER = getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    MYSQL_HOST = getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = getenv("MYSQL_PASSWORD", "password")
    MYSQL_DB = getenv("MYSQL_DB", "archivo_digital")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_AUTO_CREATE = _as_bool(getenv("DB_AUTO_CREATE", "false"), default=False)

    AZURE_STORAGE_CONNECTION_STRING = getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    AZURE_STORAGE_CONTAINER = getenv("AZURE_STORAGE_CONTAINER", "containers")
    AZURE_STORAGE_ACCOUNT_URL = getenv("AZURE_STORAGE_ACCOUNT_URL", "")

    DEFAULT_USER_IMAGE_KEY = getenv(
        "DEFAULT_USER_IMAGE_KEY", "educar/Gestion360/images/users/default-user.jpg"
    )
