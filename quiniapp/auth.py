"""Auth de la app.

Version actual: shim manual (el usuario escribe su email a mano, sin
verificacion). Pensado para probar el flujo completo sin configurar OAuth de
Google todavia.

Cuando se implemente st.login() con Google, este es el UNICO modulo que hay
que cambiar: las paginas solo llaman a get_email_actual() / esta_logueado() /
cerrar_sesion(), no acceden a st.user ni a st.session_state directamente.
"""
import streamlit as st

_SESSION_KEY = "email_actual"


def esta_logueado() -> bool:
    return bool(st.session_state.get(_SESSION_KEY))


def get_email_actual() -> str | None:
    return st.session_state.get(_SESSION_KEY)


def iniciar_sesion(email: str) -> None:
    st.session_state[_SESSION_KEY] = email.strip().lower()


def cerrar_sesion() -> None:
    st.session_state.pop(_SESSION_KEY, None)


def requerir_login() -> str:
    """Para usar al principio de cada pagina. Si no hay sesion, muestra un
    aviso y detiene la ejecucion de la pagina con st.stop().
    """
    email = get_email_actual()
    if not email:
        st.warning("Primero ingresa tu email desde la pagina principal.")
        st.stop()
    return email
