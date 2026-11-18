"""Filtro de restricciones alimentarias (tienen prioridad sobre todo lo demas)."""

# restriccion -> etiquetas de ingredientes prohibidas
RESTRICCIONES = {
    "Vegetariano": {"carne", "pescado", "marisco"},
    "Sin gluten": {"gluten"},
    "Sin lacteos": {"lacteo"},
    "Sin huevo": {"huevo"},
    "Sin mariscos": {"marisco"},
    "Sin soya": {"soya"},
    "Sin frutos secos": {"nueces"},
}


def etiquetas_prohibidas(restricciones):
    prohibidas = set()
    for r in restricciones:
        prohibidas |= RESTRICCIONES.get(r, set())
    return prohibidas


def es_prohibido(ing, prohibidas):
    tags = {t for t in ing["tags"].split(",") if t}
    return bool(tags & prohibidas)


def filtrar_receta(receta, ings, prohibidas):
    """Devuelve (receta_valida?, opcionales_omitidos).
    - Si un ingrediente ESENCIAL esta prohibido, la receta se descarta.
    - Si un OPCIONAL esta prohibido, se omite de la receta (y se avisa)."""
    for i in receta["esenciales"]:
        if es_prohibido(ings[i], prohibidas):
            return False, []
    omitidos = [i for i in receta["opcionales"] if es_prohibido(ings[i], prohibidas)]
    return True, omitidos
