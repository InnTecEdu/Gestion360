from __future__ import annotations

import mimetypes
from uuid import uuid4
from io import BytesIO
from pathlib import Path
from typing import Any, Final

from flask import current_app

try:
    from azure.storage.blob import BlobServiceClient
except ImportError:  # pragma: no cover - fallback when package not installed yet
    BlobServiceClient = None

DOCUMENTS_PREFIX: Final[str] = "educar/Gestion360/documents"
IMAGES_PREFIX: Final[str] = "educar/Gestion360/images/users"

def _is_azure_enabled() -> bool:
    has_package = BlobServiceClient is not None
    has_connection = bool(current_app.config.get("AZURE_STORAGE_CONNECTION_STRING"))
    has_container = bool(current_app.config.get("AZURE_STORAGE_CONTAINER"))
    return has_package and has_connection and has_container


def _build_blob_service() -> Any:
    if BlobServiceClient is None:
        raise RuntimeError("azure-storage-blob no está instalado")
    connection_string = current_app.config["AZURE_STORAGE_CONNECTION_STRING"]
    return BlobServiceClient.from_connection_string(connection_string)


def _local_upload_root() -> Path:
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    return Path(upload_folder)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _build_document_key(identificador: str, original_filename: str) -> str:
    extension = Path(original_filename).suffix.lower() or ".pdf"
    return f"{DOCUMENTS_PREFIX}/{identificador}/{uuid4()}{extension}"


def _build_user_image_key(username: str, original_filename: str) -> str:
    extension = Path(original_filename).suffix.lower() or ".jpg"
    safe_username = username.strip().lower().replace(" ", "_")
    return f"{IMAGES_PREFIX}/{safe_username}/{uuid4()}{extension}"


def upload_document_file(file_obj: Any, identificador: str, original_filename: str) -> str:
    storage_key = _build_document_key(identificador, original_filename)
    content_type = "application/pdf"

    if _is_azure_enabled():
        blob_service = _build_blob_service()
        container_name = current_app.config["AZURE_STORAGE_CONTAINER"]
        blob_client = blob_service.get_blob_client(container=container_name, blob=storage_key)
        file_obj.stream.seek(0)
        blob_client.upload_blob(file_obj.stream.read(), overwrite=True, content_type=content_type)
        return storage_key

    local_path = _local_upload_root() / storage_key
    _ensure_parent(local_path)
    file_obj.save(local_path)
    return storage_key


def upload_user_image(file_obj: Any, username: str, original_filename: str) -> str:
    storage_key = _build_user_image_key(username, original_filename)
    guessed_type, _ = mimetypes.guess_type(original_filename)
    content_type = guessed_type or "image/jpeg"

    if _is_azure_enabled():
        blob_service = _build_blob_service()
        container_name = current_app.config["AZURE_STORAGE_CONTAINER"]
        blob_client = blob_service.get_blob_client(container=container_name, blob=storage_key)
        file_obj.stream.seek(0)
        blob_client.upload_blob(file_obj.stream.read(), overwrite=True, content_type=content_type)
        return storage_key

    local_path = _local_upload_root() / storage_key
    _ensure_parent(local_path)
    file_obj.save(local_path)
    return storage_key


def get_file_stream(storage_key: str) -> BytesIO | None:
    if not storage_key:
        return None

    if _is_azure_enabled():
        blob_service = _build_blob_service()
        container_name = current_app.config["AZURE_STORAGE_CONTAINER"]
        blob_client = blob_service.get_blob_client(container=container_name, blob=storage_key)
        if not blob_client.exists():
            return None
        data = blob_client.download_blob().readall()
        return BytesIO(data)

    local_path = _local_upload_root() / storage_key
    if not local_path.exists():
        return None
    return BytesIO(local_path.read_bytes())


def delete_file(storage_key: str) -> None:
    if not storage_key:
        return

    if _is_azure_enabled():
        blob_service = _build_blob_service()
        container_name = current_app.config["AZURE_STORAGE_CONTAINER"]
        blob_client = blob_service.get_blob_client(container=container_name, blob=storage_key)
        if blob_client.exists():
            blob_client.delete_blob()
        return

    local_path = _local_upload_root() / storage_key
    if local_path.exists():
        local_path.unlink()


def get_file_url(storage_key: str) -> str:
    if not storage_key:
        return ""

    if _is_azure_enabled():
        account_url = current_app.config.get("AZURE_STORAGE_ACCOUNT_URL", "").rstrip("/")
        container_name = current_app.config["AZURE_STORAGE_CONTAINER"]
        if account_url:
            return f"{account_url}/{container_name}/{storage_key}"
        blob_service = _build_blob_service()
        blob_client = blob_service.get_blob_client(container=container_name, blob=storage_key)
        return blob_client.url

    return f"/{_local_upload_root().as_posix().strip('/')}/{storage_key}"
