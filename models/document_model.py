from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select

from infrastructure import db
from models.entities import Documento


def _document_to_dict(document: Documento) -> dict[str, Any]:
    return {
        "id": document.id,
        "identificador": document.identificador,
        "nombre_original": document.nombre_original,
        "nombre_guardado": document.nombre_guardado,
        "ruta": document.ruta,
        "usuario_id": document.usuario_id,
        "fecha_creacion": document.fecha_creacion,
    }


def insert_document(
    identificador: str,
    nombre_original: str,
    nombre_guardado: str,
    ruta: str,
    usuario_id: int,
) -> None:
    document = Documento()
    document.identificador = identificador
    document.nombre_original = nombre_original
    document.nombre_guardado = nombre_guardado
    document.ruta = ruta
    document.usuario_id = usuario_id
    db.session.add(document)
    db.session.commit()


def search_documents(termino: str) -> list[dict[str, Any]]:
    like_term = f"%{termino.strip()}%"
    query = (
        select(Documento)
        .where(
            or_(
                Documento.identificador == termino.strip(),
                Documento.nombre_original.ilike(like_term),
            )
        )
        .order_by(Documento.fecha_creacion.desc())
    )
    rows = db.session.execute(query).scalars().all()
    return [_document_to_dict(row) for row in rows]


def get_document_by_id(document_id: int) -> dict[str, Any] | None:
    document = db.session.get(Documento, document_id)
    return _document_to_dict(document) if document else None


def delete_document(document_id: int) -> None:
    document = db.session.get(Documento, document_id)
    if not document:
        return

    db.session.delete(document)
    db.session.commit()


def update_document(document_id: int, nombre_original: str, nombre_guardado: str, ruta: str) -> None:
    document = db.session.get(Documento, document_id)
    if not document:
        raise ValueError(f"Documento no existe: {document_id}")

    document.nombre_original = nombre_original
    document.nombre_guardado = nombre_guardado
    document.ruta = ruta
    db.session.commit()
