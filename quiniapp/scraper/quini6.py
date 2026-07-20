"""Scraper de resultados del Quini 6.

Fuente: sitio oficial de la Loteria de Santa Fe (organismo que administra el
Quini 6). La pagina publica (loteriasantafe.gov.ar) embebe un iframe que apunta
a un backend Java/JSF (PrimeFaces) que devuelve el HTML con los resultados:

    https://apps.loteriasantafe.gov.ar:8443/Extractos/paginas/mostrarQuini6.xhtml?display=0

Ese endpoint devuelve, sin parametros, el ULTIMO sorteo disponible. No hay una
API JSON: hay que parsear el HTML. Este modulo es standalone (no importa nada
de Streamlit) para poder correr como script/cron independiente.

Limitacion conocida: JSF/PrimeFaces resuelve la navegacion a sorteos previos
via postbacks AJAX con viewstate de sesion, no con una URL simple por numero
de sorteo. Por eso `scrapear_sorteo(numero)` (un sorteo especifico historico)
no esta implementado todavia -- solo se soporta traer el ultimo sorteo vigente,
que es el caso de uso real de la app (el cron corre despues de cada sorteo).
"""
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

URL_ULTIMO_SORTEO = (
    "https://apps.loteriasantafe.gov.ar:8443/Extractos/paginas/mostrarQuini6.xhtml?display=0"
)

TIMEOUT_SEGUNDOS = 15

# Nombre del <h3> en el HTML -> clave de modalidad en nuestro esquema de Mongo.
MODALIDADES = {
    "Tradicional Primer Sorteo": "tradicional",
    "Tradicional La Segunda del Quini": "segunda",
    "Revancha": "revancha",
    "Siempre Sale": "siempre_sale",
}

MESES_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11,
    "diciembre": 12,
}


class ScrapingError(Exception):
    """El HTML de la fuente no tiene la estructura esperada (cambio de sitio)."""


def _parse_numero_y_dia(texto_opcion: str) -> tuple[int, int]:
    """Parsea algo como 'Domingo 19 - 3392' -> (numero_sorteo=3392, dia=19)."""
    match = re.match(r".+?\s+(\d+)\s*-\s*(\d+)", texto_opcion)
    if not match:
        raise ScrapingError(f"No se pudo parsear numero/dia de sorteo: {texto_opcion!r}")
    dia, numero = match.groups()
    return int(numero), int(dia)


def _parse_mes_anio(texto_opcion: str) -> tuple[int, int]:
    """Parsea 'Julio 2026' -> (mes=7, anio=2026)."""
    match = re.match(r"(\w+)\s+(\d{4})", texto_opcion.strip())
    if not match:
        raise ScrapingError(f"No se pudo parsear mes/anio: {texto_opcion!r}")
    nombre_mes, anio = match.groups()
    mes = MESES_ES.get(nombre_mes.lower())
    if mes is None:
        raise ScrapingError(f"Mes desconocido: {nombre_mes!r}")
    return mes, int(anio)


def _extraer_numeros(bloque) -> list[int]:
    """Extrae los 6 numeros de un bloque <div class='contenedorquini1'>.

    Los numeros de las 4 modalidades principales usan la clase 'cuadrado'
    (a diferencia del Premio Extra, que usa 'cuadradoPE'/'cuadradoPET' y que
    no nos interesa porque es derivable de las otras 3).
    """
    celdas = bloque.select("div.cuadrado b")
    numeros = [int(c.get_text(strip=True)) for c in celdas]
    if len(numeros) != 6:
        raise ScrapingError(f"Se esperaban 6 numeros, se encontraron {len(numeros)}")
    return numeros


def _parsear_html(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    select_sorteo = soup.select_one("#form\\:sorteoSeleccionado_input")
    if select_sorteo is None:
        raise ScrapingError("No se encontro el selector de sorteo en el HTML")
    primera_opcion = select_sorteo.find("option")
    if primera_opcion is None:
        raise ScrapingError("El selector de sorteo no tiene opciones")
    numero, dia = _parse_numero_y_dia(primera_opcion.get_text(strip=True))

    select_mes = soup.select_one("#form\\:mesSeleccionado_input")
    if select_mes is None:
        raise ScrapingError("No se encontro el selector de mes en el HTML")
    opcion_mes = select_mes.select_one("option[selected]") or select_mes.find("option")
    mes, anio = _parse_mes_anio(opcion_mes.get_text(strip=True))

    fecha = datetime(anio, mes, dia, tzinfo=timezone.utc)

    resultados: dict[str, list[int]] = {}
    for bloque in soup.select("div.contenedorquini1"):
        titulo_tag = bloque.find("h3")
        if titulo_tag is None:
            continue
        titulo = titulo_tag.get_text(strip=True)
        modalidad = MODALIDADES.get(titulo)
        if modalidad is None:
            continue  # p.ej. "Premio Extra", que no persistimos
        resultados[modalidad] = _extraer_numeros(bloque)

    faltantes = set(MODALIDADES.values()) - set(resultados.keys())
    if faltantes:
        raise ScrapingError(f"Faltan modalidades en el HTML: {faltantes}")

    return {"numero": numero, "fecha": fecha, "resultados": resultados}


def scrapear_ultimo_sorteo() -> dict:
    """Trae y parsea el ultimo sorteo publicado.

    Devuelve {"numero": int, "fecha": datetime, "resultados": {...}}.
    Lanza requests.RequestException si falla la conexion, o ScrapingError
    si la estructura del HTML no es la esperada.
    """
    respuesta = requests.get(URL_ULTIMO_SORTEO, timeout=TIMEOUT_SEGUNDOS)
    respuesta.raise_for_status()
    return _parsear_html(respuesta.text)


def scrapear_sorteo(numero: int) -> dict | None:
    raise NotImplementedError(
        "Scrapear un sorteo historico especifico requiere simular postbacks "
        "AJAX de JSF (viewstate + sesion), no una URL simple. No implementado."
    )
