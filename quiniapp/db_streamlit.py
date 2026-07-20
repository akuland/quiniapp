"""Wrapper cacheado de db.py para uso exclusivo dentro de la app Streamlit.

El scraper standalone NO debe importar este modulo (no tiene runtime de
Streamlit disponible); debe usar quiniapp.db directamente.
"""
import streamlit as st
from pymongo.database import Database

from quiniapp.db import get_client, get_db


@st.cache_resource
def get_cached_client():
    return get_client()


def get_app_db() -> Database:
    return get_db(get_cached_client())
