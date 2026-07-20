"""Operaciones sobre la coleccion usuarios (patron embedding: 1 doc por usuario)."""
from datetime import datetime, timezone

from bson import ObjectId
from pymongo.database import Database

from quiniapp.models import normalizar_numeros, validar_numeros


def get_usuario(db: Database, email: str) -> dict | None:
    return db.usuarios.find_one({"email": email})


def get_boletas(db: Database, email: str, solo_activas: bool = True) -> list[dict]:
    usuario = get_usuario(db, email)
    if not usuario:
        return []
    boletas = usuario.get("boletas", [])
    if solo_activas:
        boletas = [b for b in boletas if b.get("activa", True)]
    return boletas


def agregar_boleta(db: Database, email: str, numeros: list[int], alias: str = "") -> ObjectId:
    validar_numeros(numeros)
    boleta = {
        "_id": ObjectId(),
        "numeros": normalizar_numeros(numeros),
        "alias": alias,
        "activa": True,
    }
    db.usuarios.update_one(
        {"email": email},
        {
            "$push": {"boletas": boleta},
            "$set": {"fecha_actualizacion": datetime.now(timezone.utc)},
            "$setOnInsert": {"email": email},
        },
        upsert=True,
    )
    return boleta["_id"]


def borrar_boleta(db: Database, email: str, boleta_id: ObjectId) -> None:
    db.usuarios.update_one(
        {"email": email},
        {
            "$pull": {"boletas": {"_id": boleta_id}},
            "$set": {"fecha_actualizacion": datetime.now(timezone.utc)},
        },
    )


def archivar_boleta(db: Database, email: str, boleta_id: ObjectId, activa: bool = False) -> None:
    db.usuarios.update_one(
        {"email": email, "boletas._id": boleta_id},
        {
            "$set": {
                "boletas.$.activa": activa,
                "fecha_actualizacion": datetime.now(timezone.utc),
            }
        },
    )


def asegurar_indices(db: Database) -> None:
    db.usuarios.create_index("email", unique=True)
