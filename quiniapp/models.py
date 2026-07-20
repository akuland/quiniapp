"""Validaciones y helpers de armado de documentos. Sin dependencias de Mongo ni Streamlit."""
from typing import TypedDict

NUMERO_MIN = 0
NUMERO_MAX = 45
CANTIDAD_NUMEROS = 6


class Boleta(TypedDict):
    _id: object  # ObjectId
    numeros: list[int]
    alias: str
    activa: bool


class ResultadosSorteo(TypedDict):
    tradicional: list[int]
    segunda: list[int]
    revancha: list[int]
    siempre_sale: list[int]


def validar_numeros(numeros: list[int]) -> None:
    """Lanza ValueError si los numeros no cumplen el formato de una jugada de Quini 6."""
    if len(numeros) != CANTIDAD_NUMEROS:
        raise ValueError(f"Una boleta debe tener {CANTIDAD_NUMEROS} numeros")
    if len(set(numeros)) != CANTIDAD_NUMEROS:
        raise ValueError("Los numeros de una boleta no pueden repetirse")
    for n in numeros:
        if not (NUMERO_MIN <= n <= NUMERO_MAX):
            raise ValueError(f"Cada numero debe estar entre {NUMERO_MIN} y {NUMERO_MAX}")


def normalizar_numeros(numeros: list[int]) -> list[int]:
    """Ordena ascendente antes de guardar, para simplificar visualizacion y comparacion."""
    return sorted(numeros)
