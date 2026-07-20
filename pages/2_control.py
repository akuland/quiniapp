import streamlit as st

from quiniapp.auth import requerir_login
from quiniapp.db_streamlit import get_app_db
from quiniapp.logica.control import calcular_aciertos, evaluar_premios
from quiniapp.repositories.sorteos import get_sorteo, get_ultimo_sorteo
from quiniapp.repositories.usuarios import get_boletas

NOMBRES_MODALIDAD = {
    "tradicional": "Tradicional",
    "segunda": "Segunda",
    "revancha": "Revancha",
    "siempre_sale": "Siempre Sale",
    "premio_extra": "Premio Extra",
}

email = requerir_login()
db = get_app_db()

st.title("Control de aciertos")

ultimo_sorteo = get_ultimo_sorteo(db)
if not ultimo_sorteo:
    st.info("Todavia no hay sorteos cargados en la base.")
    st.stop()

numero_sorteo = st.number_input(
    "Numero de sorteo", min_value=1, value=ultimo_sorteo["_id"], step=1
)
sorteo = get_sorteo(db, numero_sorteo)

if not sorteo:
    st.warning(f"No hay datos del sorteo {numero_sorteo} en la base.")
    st.stop()

boletas = get_boletas(db, email, solo_activas=True)
if not boletas:
    st.info("Todavia no cargaste ninguna boleta.")
    st.stop()

for boleta in boletas:
    aciertos = calcular_aciertos(boleta, sorteo)
    premios = evaluar_premios(aciertos)
    etiqueta = boleta["alias"] or "Sin alias"

    if any(premios.values()):
        st.subheader(f"🎉 {etiqueta} — {boleta['numeros']}")
    else:
        st.subheader(f"{etiqueta} — {boleta['numeros']}")

    for modalidad, cantidad in aciertos.items():
        nombre = NOMBRES_MODALIDAD[modalidad]
        if premios[modalidad]:
            st.markdown(
                f":green[**{nombre}: {cantidad} aciertos — ¡PREMIADA!**]"
            )
        else:
            st.write(f"{nombre}: {cantidad} aciertos")
