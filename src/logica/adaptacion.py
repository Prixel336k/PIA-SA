"""Mecanismo de adaptacion: RELAJACION PROGRESIVA de criterios.

Cada vez que cambia la despensa, el antojo o las restricciones, el sistema vuelve a
evaluar TODO el catalogo y decide con que nivel de exigencia puede responder:

  Nivel 1  Cocina elegida, compatibilidad >= 60 % y todos los esenciales cubiertos
  Nivel 2  Cocina elegida, compatibilidad >= 40 % (acepta que falten ingredientes)
  Nivel 3  Se amplia a OTRAS cocinas, compatibilidad >= 60 % y esenciales cubiertos
  Nivel 4  Mejores opciones disponibles de cualquier cocina, con lista de compras

Asi el sistema siempre devuelve una opcion viable y explica que ajuste hizo.
Con 'Sorprendeme' (sin cocina) se evalua todo el catalogo desde el nivel 1.
"""
from .puntuacion import evaluar_receta
from .restricciones import etiquetas_prohibidas

UMBRAL_ALTO = 60.0
UMBRAL_BAJO = 40.0
MAX_RESULTADOS = 8
SORPRENDEME = "Sorprendeme"


def _ordenar(lista):
    return sorted(lista, key=lambda e: (-e["score"], e["receta"]["nombre"]))


def recomendar(catalogo, despensa, antojo, restricciones):
    """catalogo = (ings, recetas, subs). Devuelve dict(nivel, mensaje, resultados)."""
    ings, recetas, subs = catalogo
    prohibidas = etiquetas_prohibidas(restricciones)
    despensa = set(despensa)

    evals = [e for e in (evaluar_receta(r, despensa, ings, subs, prohibidas)
                         for r in recetas.values()) if e]
    descartadas = len(recetas) - len(evals)

    if not despensa:
        return {"nivel": 0, "descartadas": descartadas, "resultados": [],
                "mensaje": "Tu despensa esta vacia. Marca los ingredientes que tienes."}
    if not evals:
        return {"nivel": 0, "descartadas": descartadas, "resultados": [],
                "mensaje": "Las restricciones indicadas descartan todas las recetas del catalogo."}

    libre = antojo in ("", SORPRENDEME, None)
    de_cocina = evals if libre else [e for e in evals if e["receta"]["cocina"] == antojo]
    otras = [] if libre else [e for e in evals if e["receta"]["cocina"] != antojo]
    nombre = "todas las cocinas" if libre else f"cocina {antojo}"

    def dar(nivel, msg, lista):
        return {"nivel": nivel, "mensaje": msg, "descartadas": descartadas,
                "resultados": _ordenar(lista)[:MAX_RESULTADOS]}

    n1 = [e for e in de_cocina if e["score"] >= UMBRAL_ALTO and e["cocinable"]]
    if n1:
        return dar(1, f"Nivel 1: encontre platillos de {nombre} que ya puedes preparar.", n1)

    n2 = [e for e in de_cocina if e["score"] >= UMBRAL_BAJO]
    if n2:
        return dar(2, f"Nivel 2: ningun platillo de {nombre} esta completo; relaje la exigencia "
                      f"a {UMBRAL_BAJO:.0f}% y te muestro los que mas se acercan (te faltan ingredientes).", n2)

    n3 = [e for e in otras if e["score"] >= UMBRAL_ALTO and e["cocinable"]]
    if n3:
        return dar(3, f"Nivel 3: con tu despensa no alcanza para {nombre}. Amplie la busqueda a "
                      f"otras cocinas y encontre estas opciones viables.", n3)

    return dar(4, "Nivel 4: tu despensa tiene pocos ingredientes para cualquier cocina. Estas son las "
                  "opciones mas cercanas; revisa que te falta comprar.", evals)


def cocinar(con_estado, resultado):
    """Al cocinar un platillo se gastan sus ingredientes (no los basicos). Devuelve los ids a quitar."""
    usados = set(resultado["tengo"]) | {s for _, s in resultado["sustituidos"]}
    return usados
