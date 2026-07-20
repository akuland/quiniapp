"""Conexion a MongoDB. Un solo cliente reutilizado por toda la app."""
import os

from pymongo import MongoClient
from pymongo.database import Database


def get_client(uri: str | None = None) -> MongoClient:
    """Crea un MongoClient a partir de una URI.

    Si no se pasa `uri`, la toma de la variable de entorno MONGO_URI (uso
    standalone: scraper, scripts de cron). La app de Streamlit resuelve la
    URI desde st.secrets y la pasa explicitamente (ver db_streamlit.py),
    porque Streamlit Cloud no inyecta los secrets en os.environ.

    No usa st.cache_resource aca para que este modulo tambien pueda
    importarse desde el scraper standalone (sin runtime de Streamlit).
    El cacheo para la app de Streamlit se hace en el caller.
    """
    uri = uri or os.environ["MONGO_URI"]
    return MongoClient(uri)


def get_db(client: MongoClient | None = None, db_name: str | None = None) -> Database:
    db_name = db_name or os.environ.get("MONGO_DB_NAME", "quiniapp")
    client = client or get_client()
    return client[db_name]
