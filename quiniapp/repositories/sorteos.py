"""Operaciones sobre la coleccion sorteos (1 doc por sorteo, _id = numero de sorteo)."""
from datetime import datetime, timezone

from pymongo.database import Database


def existe_sorteo(db: Database, numero: int) -> bool:
    return db.sorteos.find_one({"_id": numero}, {"_id": 1}) is not None


def get_sorteo(db: Database, numero: int) -> dict | None:
    return db.sorteos.find_one({"_id": numero})


def get_ultimo_sorteo(db: Database) -> dict | None:
    return db.sorteos.find_one(sort=[("_id", -1)])


def guardar_sorteo(db: Database, numero: int, fecha: datetime, resultados: dict) -> None:
    """Inserta o reemplaza un sorteo. resultados debe tener las 4 modalidades
    (tradicional, segunda, revancha, siempre_sale) con listas de 6 numeros.
    """
    db.sorteos.update_one(
        {"_id": numero},
        {
            "$set": {
                "fecha": fecha,
                "resultados": resultados,
                "scrapeado_en": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )
