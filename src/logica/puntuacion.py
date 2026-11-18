"""Motor de puntuacion: que tan bien coincide una receta con la despensa.

Compatibilidad (0-100):
    ingrediente esencial  -> peso 2
    ingrediente opcional  -> peso 1
    lo tienes             -> 100% de su peso
    lo cubre un sustituto -> 60% de su peso
    no lo tienes          -> 0%
Los ingredientes basicos (sal, aceite, agua...) no cuentan.
"""
from .restricciones import filtrar_receta
from .sustitutos import buscar_sustituto, sugerencias_compra

PESO_ESENCIAL = 2
PESO_OPCIONAL = 1
FACTOR_SUSTITUTO = 0.6


def evaluar_receta(receta, despensa, ings, subs, prohibidas):
    """Devuelve un dict con el analisis de la receta, o None si la restriccion la descarta."""
    valida, omitidos = filtrar_receta(receta, ings, prohibidas)
    if not valida:
        return None

    total = obtenido = 0.0
    tengo, sustituidos, faltan = [], [], []   # sustituidos: (faltante, sustituto)

    def procesar(lista, peso, es_esencial):
        nonlocal total, obtenido
        for i in lista:
            if ings[i]["basico"] or i in omitidos:
                continue
            total += peso
            if i in despensa:
                obtenido += peso
                tengo.append(i)
                continue
            s = buscar_sustituto(i, despensa, subs, ings, prohibidas)
            if s is not None:
                obtenido += peso * FACTOR_SUSTITUTO
                sustituidos.append((i, s))
            else:
                faltan.append((i, es_esencial, sugerencias_compra(i, subs, ings, prohibidas)))

    procesar(receta["esenciales"], PESO_ESENCIAL, True)
    procesar(receta["opcionales"], PESO_OPCIONAL, False)

    score = round(100 * obtenido / total, 1) if total else 0.0
    faltan_esenciales = [f for f in faltan if f[1]]
    return {
        "receta": receta,
        "score": score,
        "tengo": tengo,
        "sustituidos": sustituidos,
        "faltan": faltan,
        "faltan_esenciales": faltan_esenciales,
        "omitidos": omitidos,
        "cocinable": len(faltan_esenciales) == 0,
    }
