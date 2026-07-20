# Quini 6 - Control de boletas

App para cargar tus boletas del Quini 6 y controlar automáticamente los
aciertos contra los resultados oficiales de cada sorteo.

## Funcionalidad

- Cargar varias boletas (6 números entre 0 y 45 cada una), con alias opcional.
- Borrar boletas cargadas.
- Ver, para cualquier sorteo guardado, los aciertos de cada boleta en las
  4 modalidades (Tradicional, Segunda, Revancha, Siempre Sale) y en el
  Premio Extra. Las boletas premiadas se resaltan en verde.
- Scraper que trae el último sorteo publicado desde el sitio oficial de la
  Lotería de Santa Fe y lo cachea en MongoDB (no vuelve a scrapear un sorteo
  que ya está guardado).

## Stack

- [Streamlit](https://streamlit.io/) para la interfaz web.
- [MongoDB](https://www.mongodb.com/) para persistencia (patrón de embedding:
  un documento por usuario con sus boletas embebidas; un documento por sorteo).
- [PyMongo](https://pymongo.readthedocs.io/) como driver.
- `requests` + `BeautifulSoup` para el scraper de resultados.

## Estructura del proyecto

```
quiniapp/
├── streamlit_app.py             # entry point de Streamlit
├── pages/
│   ├── 1_mis_boletas.py        # cargar / listar / borrar boletas
│   └── 2_control.py            # elegir sorteo y ver aciertos
├── quiniapp/                   # paquete con la lógica, sin nada de UI
│   ├── auth.py                  # manejo de sesión / identidad del usuario
│   ├── db.py                    # conexión a Mongo (uso standalone)
│   ├── db_streamlit.py          # wrapper cacheado para la app Streamlit
│   ├── models.py                # validación de boletas
│   ├── repositories/            # acceso a datos (usuarios, sorteos)
│   ├── logica/                  # cálculo de aciertos y premios
│   └── scraper/                 # scraping de resultados
└── scripts/
    └── actualizar_sorteos.py    # script standalone (pensado para cron)
```

## Modelo de datos

**`sorteos`** — un documento por sorteo, `_id` = número de sorteo:

```json
{
  "_id": 3392,
  "fecha": "2026-07-19T00:00:00Z",
  "resultados": {
    "tradicional": [5, 17, 27, 28, 31, 45],
    "segunda": [8, 21, 23, 33, 36, 41],
    "revancha": [4, 10, 14, 17, 25, 32],
    "siempre_sale": [4, 14, 18, 19, 28, 29]
  },
  "scrapeado_en": "2026-07-20T16:17:17Z"
}
```

**`usuarios`** — un documento por usuario, con las boletas embebidas:

```json
{
  "_id": "ObjectId(...)",
  "email": "usuario@gmail.com",
  "boletas": [
    { "_id": "ObjectId(...)", "numeros": [1, 2, 3, 5, 17, 27], "alias": "Boleta 1", "activa": true }
  ],
  "fecha_actualizacion": "2026-07-20T18:30:00Z"
}
```

El Premio Extra (combinación de tradicional + segunda + revancha) se calcula
al vuelo, no se persiste, para evitar desincronización.

## Configuración local

1. Cloná el repo e instalá las dependencias:

   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copiá `.env.example` a `.env` y completá `MONGO_URI` con tu conexión a Mongo
   (local o Atlas):

   ```
   MONGO_URI=mongodb://localhost:27017/?replicaSet=rs0
   MONGO_DB_NAME=quiniapp-db
   ```

3. Corré la app:

   ```
   streamlit run streamlit_app.py
   ```

4. (Opcional) Para traer el último sorteo real y guardarlo en Mongo:

   ```
   python scripts/actualizar_sorteos.py
   ```

## Estado del login

Por ahora el login es un formulario simple donde escribís tu email a mano
(sin verificación), pensado para probar el flujo completo sin depender de
credenciales de OAuth. Ver `quiniapp/auth.py` — es el único módulo a
reemplazar el día que se integre login real con Google (`st.login()`), que
requiere completar `.streamlit/secrets.toml` (ver `secrets.toml.example`).

## Limitaciones conocidas

- El scraper solo puede traer el **último sorteo publicado**. Traer un sorteo
  histórico puntual requeriría simular la navegación AJAX del sitio de origen
  (JSF/PrimeFaces con viewstate de sesión), fuera de alcance por ahora.
- El umbral de "premio" en la modalidad *Siempre Sale* es una aproximación
  (4+ aciertos). La regla real es en cascada según haya o no ganadores en
  los niveles superiores del sorteo completo, dato que no se persiste.
