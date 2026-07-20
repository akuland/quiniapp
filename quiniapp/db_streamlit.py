"""Wrapper cacheado de db.py para uso exclusivo dentro de la app Streamlit.

El scraper standalone NO debe importar este modulo (no tiene runtime de
Streamlit disponible); debe usar quiniapp.db directamente.

Resuelve MONGO_URI / MONGO_DB_NAME desde st.secrets (Streamlit Community
Cloud) con fallback a variables de entorno (uso local con .env), porque
Streamlit Cloud no inyecta los secrets configurados en el panel a
os.environ automaticamente.
"""
import os

import streamlit as st
from pymongo.database import Database

from quiniapp.db import get_client, get_db


def _get_config(key: str, default: str | None = None) -> str | None:
    if key in st.secrets:
        return st.secrets[key]
    return os.environ.get(key, default)


@st.cache_resource
def get_cached_client():
    uri = _get_config("MONGO_URI")
    if not uri:
        raise RuntimeError(
            "Falta MONGO_URI. Configuralo en .env (local) o en Secrets "
            "(Streamlit Community Cloud)."
        )
    return get_client(uri)


def get_app_db() -> Database:
    db_name = _get_config("MONGO_DB_NAME", "quiniapp")
    return get_db(get_cached_client(), db_name)
