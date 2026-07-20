import streamlit as st

from quiniapp.auth import requerir_login
from quiniapp.db_streamlit import get_app_db
from quiniapp.models import CANTIDAD_NUMEROS, NUMERO_MAX, NUMERO_MIN
from quiniapp.repositories.usuarios import agregar_boleta, borrar_boleta, get_boletas

email = requerir_login()
db = get_app_db()

st.title("Mis boletas")

with st.form("nueva_boleta", clear_on_submit=True):
    st.write(f"Elegi {CANTIDAD_NUMEROS} numeros entre {NUMERO_MIN} y {NUMERO_MAX}")
    numeros = st.multiselect(
        "Numeros",
        options=list(range(NUMERO_MIN, NUMERO_MAX + 1)),
        max_selections=CANTIDAD_NUMEROS,
    )
    alias = st.text_input("Alias (opcional)")
    submitted = st.form_submit_button("Agregar boleta")

    if submitted:
        try:
            agregar_boleta(db, email, numeros, alias)
            st.success("Boleta agregada.")
        except ValueError as e:
            st.error(str(e))

st.divider()

boletas = get_boletas(db, email, solo_activas=True)
if not boletas:
    st.info("Todavia no cargaste ninguna boleta.")
else:
    for boleta in boletas:
        col1, col2 = st.columns([4, 1])
        etiqueta = boleta["alias"] or "Sin alias"
        col1.write(f"**{etiqueta}** — {boleta['numeros']}")
        if col2.button("Borrar", key=str(boleta["_id"])):
            borrar_boleta(db, email, boleta["_id"])
            st.rerun()
