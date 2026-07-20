"""Calculo de aciertos y pozo extra. Puro Python, sin Mongo ni Streamlit."""

# Aciertos minimos para considerar una boleta premiada en cada modalidad,
# segun reglas.md. Para "siempre_sale" es una simplificacion: la regla real
# es en cascada (6, si no hay entonces 5, si no hay entonces 4) y depende de
# si hubo ganadores en el nivel superior en TODO el sorteo, dato que no
# persistimos en Mongo. Acá marcamos premiado con 4+ aciertos, que puede ser
# optimista en algun caso borde.
UMBRAL_PREMIO = {
    "tradicional": 4,
    "segunda": 4,
    "revancha": 6,
    "siempre_sale": 4,
    "premio_extra": 6,
}


def evaluar_premios(aciertos: dict[str, int]) -> dict[str, bool]:
    """Indica, por modalidad, si la cantidad de aciertos alcanza el umbral de premio."""
    return {
        modalidad: cantidad >= UMBRAL_PREMIO[modalidad]
        for modalidad, cantidad in aciertos.items()
    }


def pozo_extra(resultados: dict) -> set[int]:
    """El Premio Extra combina tradicional + segunda + revancha (regla del Quini 6)."""
    return set(resultados["tradicional"]) | set(resultados["segunda"]) | set(resultados["revancha"])


def calcular_aciertos(boleta: dict, sorteo: dict) -> dict[str, int]:
    """Devuelve la cantidad de aciertos de una boleta contra cada modalidad de un sorteo."""
    numeros_boleta = set(boleta["numeros"])
    resultados = sorteo["resultados"]

    aciertos = {
        modalidad: len(numeros_boleta & set(numeros_ganadores))
        for modalidad, numeros_ganadores in resultados.items()
    }
    aciertos["premio_extra"] = len(numeros_boleta & pozo_extra(resultados))
    return aciertos
