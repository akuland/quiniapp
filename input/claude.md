Como te imaginas la base Mongo?


Estructuró colecciones y documentos MongoDB con ejemplos JSON
Estructuró colecciones y documentos MongoDB con ejemplos JSON
Me la imagino con dos colecciones, aprovechando que Mongo te deja anidar estructuras sin necesidad de joins:

Colección boletas

json
{
  "_id": ObjectId("..."),
  "email": "facu@gmail.com",
  "numeros": [4, 12, 19, 23, 38, 45],
  "sorteo_desde": 3345,
  "sorteo_hasta": 3350,
  "fecha_carga": ISODate("2026-07-20T18:30:00Z"),
  "activa": true,
  "alias": "Boleta de la oficina"
}
Detalles de diseño:

email viene de st.user.email y es tu filtro principal — índice sobre este campo.
numeros siempre ordenado ascendente al guardar; simplifica la visualización y la comparación.
sorteo_desde / sorteo_hasta porque en Quini 6 podés jugar la misma boleta hasta varios sorteos futuros. Si jugó uno solo, ambos valen lo mismo.
activa para "archivar" boletas viejas sin borrarlas.
alias opcional, útil cuando tenés varias.
Colección sorteos

json
{
  "_id": 3345,
  "fecha": ISODate("2026-07-19T21:00:00Z"),
  "resultados": {
    "tradicional": [2, 11, 15, 28, 33, 41],
    "segunda": [5, 9, 22, 30, 36, 44],
    "revancha": [1, 8, 17, 25, 39, 42],
    "siempre_sale": [3, 14, 20, 27, 35, 40]
  },
  "pozo_extra": [2, 11, 15, 28, 33, 41, 5, 9, 22, 30],
  "scrapeado_en": ISODate("2026-07-20T10:00:00Z")
}
Detalles:

Uso el número de sorteo como _id directamente — es un identificador natural, único, y te ahorra un índice extra. Buscar "el sorteo 3345" es un lookup directo.
resultados anidado por modalidad, así la lógica de control itera sobre las claves.
pozo_extra aparte porque funciona distinto (combina números de las modalidades y paga con 6 aciertos entre esos).
scrapeado_en te sirve para cachear: si el sorteo ya está en Mongo, no volvés a scrapear.
La consulta clave de la app queda simple: boletas del usuario donde sorteo_desde <= X <= sorteo_hasta:

python
db.boletas.find({
    "email": st.user.email,
    "activa": True,
    "sorteo_desde": {"$lte": nro_sorteo},
    "sorteo_hasta": {"$gte": nro_sorteo}
})
Y el control de aciertos se hace en Python en memoria — son pocas boletas por usuario, no vale la pena complicarse con aggregation pipelines.

Único índice adicional que crearía: compuesto sobre {email: 1, activa: 1} en boletas. Con el tier M0 de Atlas vas sobrado.

¿Te cierra? Si querés, el próximo paso es el scraper de resultados, que es la parte con más incógnitas.

La colección boletas, yo quiero poder cargar varias boletas, no una sola, no importa para nada los sorteos desde/hasta


Restructuró esquema para múltiples boletas sin rangos sorteo
Restructuró esquema para múltiples boletas sin rangos sorteo
Sin problema — cada documento es una boleta, y podés tener tantas como quieras. Simplemente saco los campos de sorteos y queda así:

json
{
  "_id": ObjectId("..."),
  "email": "facu@gmail.com",
  "numeros": [4, 12, 19, 23, 38, 45],
  "alias": "Boleta 1",
  "fecha_carga": ISODate("2026-07-20T18:30:00Z"),
  "activa": true
}
Cargás 5 boletas → 5 documentos con tu email. La consulta se reduce a:

python
boletas = db.boletas.find({"email": st.user.email, "activa": True})
Y el control cruza todas tus boletas activas contra el sorteo que elijas (por defecto el último):

python
for boleta in boletas:
    for modalidad, resultado in sorteo["resultados"].items():
        aciertos = len(set(boleta["numeros"]) & set(resultado))
En la UI de carga podés tener un formulario que te deje agregar varias de una: cargás 6 números, "Agregar otra", y al final un solo botón que inserta todas con insert_many.

activa lo mantendría igual — cuando una boleta ya no juega más, la archivás y no aparece en el control, pero conservás el historial. Si ni eso te interesa, se borra directamente con un botón de eliminar y listo.

¿Así te cierra? Siguiente paso lógico: el scraper de resultados.

Si en vez de cargar 5 documentos, cargo 1 solo con mi email y un array de n boletas?


Sopesó ventajas de simplicidad contra inconvenientes de mantenimiento
Sopesó ventajas de simplicidad contra inconvenientes de mantenimiento
Se puede, y para esta escala funciona perfectamente. Quedaría así:

json
{
  "_id": "facu@gmail.com",
  "boletas": [
    {
      "id": 1,
      "numeros": [4, 12, 19, 23, 38, 45],
      "alias": "Boleta 1",
      "activa": true
    },
    {
      "id": 2,
      "numeros": [7, 13, 21, 29, 34, 44],
      "alias": "Boleta 2",
      "activa": true
    }
  ],
  "fecha_actualizacion": ISODate("2026-07-20T18:30:00Z")
}
Fijate que acá el email puede ser directamente el _id — un documento por usuario, lookup directo, sin índices extra. Un solo find_one trae todo lo tuyo. Es el patrón embedding clásico de Mongo y encaja bien porque las boletas no tienen vida propia fuera del usuario.

Los trade-offs, para que decidas con toda la información:

A favor del array embebido: una sola lectura por usuario, modelo más simple, cero índices adicionales, y el documento de un usuario típico (¿10, 20 boletas?) pesa nada.

En contra: modificar una boleta puntual requiere operadores de array ($push para agregar, $pull para borrar, arrayFilters para editar una específica), que son un poco más verbosos que un update_one sobre un documento propio. Necesitás generar vos el id interno de cada boleta (un contador o un uuid4). Y si algún día quisieras consultar boletas cruzando usuarios ("¿cuántas boletas jugaron el 45?"), es más incómodo — aunque para tu caso eso no existe.

Ejemplo de las operaciones típicas:

python
# Agregar boleta
db.usuarios.update_one(
    {"_id": email},
    {"$push": {"boletas": nueva_boleta}},
    upsert=True  # crea el doc si es tu primera boleta
)

# Borrar boleta por id
db.usuarios.update_one(
    {"_id": email},
    {"$pull": {"boletas": {"id": boleta_id}}}
)
El límite de 16 MB por documento en Mongo acá es irrelevante — entrarían decenas de miles de boletas.

Para tu caso de uso concreto, con pocos usuarios y pocas boletas cada uno, iría con tu propuesta: es más simple conceptualmente y la app siempre lee "todas mis boletas" de una. La versión de un documento por boleta gana recién cuando las boletas necesitan ciclo de vida propio o volumen grande.