import streamlit as st
from dotenv import load_dotenv

from quiniapp.auth import cerrar_sesion, esta_logueado, get_email_actual, iniciar_sesion

load_dotenv()

st.set_page_config(page_title="Quini 6", page_icon="🎱")

st.title("Quini 6 - Control de boletas")

if not esta_logueado():
    st.write(
        "Version de prueba sin login real: escribi tu email para identificar "
        "tus boletas. Mas adelante esto se reemplaza por login con Google."
    )
    email = st.text_input("Tu email")
    if st.button("Continuar") and email.strip():
        iniciar_sesion(email)
        st.rerun()
    st.stop()

st.sidebar.write(f"Conectado como {get_email_actual()}")
if st.sidebar.button("Cerrar sesion"):
    cerrar_sesion()
    st.rerun()

st.write("Usa el menu de la izquierda para cargar boletas o controlar aciertos.")
