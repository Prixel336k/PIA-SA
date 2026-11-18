"""Sustitucion: busca alternativas para un ingrediente faltante usando la despensa."""
from .restricciones import es_prohibido


def buscar_sustituto(ing_id, despensa, subs, ings, prohibidas):
    """Devuelve el id de un sustituto que el usuario YA tiene y que respeta sus
    restricciones, o None."""
    for s in subs.get(ing_id, []):
        if s in despensa and not es_prohibido(ings[s], prohibidas):
            return s
    return None


def sugerencias_compra(ing_id, subs, ings, prohibidas):
    """Sustitutos posibles (aunque el usuario no los tenga) que respetan restricciones."""
    return [s for s in subs.get(ing_id, []) if not es_prohibido(ings[s], prohibidas)]
