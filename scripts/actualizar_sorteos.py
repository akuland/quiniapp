"""Script standalone (pensado para cron) que scrapea el ultimo sorteo y lo
guarda en Mongo si todavia no esta cacheado. No depende de Streamlit.

Uso: python scripts/actualizar_sorteos.py
"""
from dotenv import load_dotenv

from quiniapp.db import get_db
from quiniapp.repositories.sorteos import existe_sorteo, guardar_sorteo
from quiniapp.scraper.quini6 import scrapear_ultimo_sorteo


def main() -> None:
    load_dotenv()
    db = get_db()

    resultado = scrapear_ultimo_sorteo()
    if resultado is None:
        print("No se encontro ningun sorteo nuevo.")
        return

    if existe_sorteo(db, resultado["numero"]):
        print(f"Sorteo {resultado['numero']} ya estaba cacheado, no se vuelve a scrapear.")
        return

    guardar_sorteo(db, resultado["numero"], resultado["fecha"], resultado["resultados"])
    print(f"Sorteo {resultado['numero']} guardado.")


if __name__ == "__main__":
    main()
