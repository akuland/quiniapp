"""Conexion a MongoDB. Un solo cliente reutilizado por toda la app."""
import os

from pymongo import MongoClient
from pymongo.database import Database


def get_client() -> MongoClient:
    """Crea un MongoClient a partir de MONGO_URI.

    No usa st.cache_resource aca para que este modulo tambien pueda
    importarse desde el scraper standalone (sin runtime de Streamlit).
    El cacheo para la app de Streamlit se hace en el caller (ver
    quiniapp/db_streamlit.py).
    """
    uri = os.environ["MONGO_URI"]
    return MongoClient(uri)


def get_db(client: MongoClient | None = None) -> Database:
    db_name = os.environ.get("MONGO_DB_NAME", "quiniapp")
    client = client or get_client()
    return client[db_name]
