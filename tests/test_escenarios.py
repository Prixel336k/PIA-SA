"""Escenarios de prueba del sistema (evidencia para la Evidencia 3).
Ejecutar:  python tests/test_escenarios.py        (muestra los resultados)
           python -m unittest discover tests      (corre las pruebas)
"""
import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

import db
from logica.adaptacion import recomendar, SORPRENDEME


def despensa_por_nombre(con, nombres):
    ids = {r["nombre"]: r["id"] for r in con.execute("SELECT id,nombre FROM ingredientes")}
    return {ids[n] for n in nombres}


def mostrar(titulo, cat, res):
    ings = cat[0]
    print(f"\n=== {titulo} ===")
    print(res["mensaje"])
    for e in res["resultados"][:5]:
        f = ", ".join(ings[i]["nombre"] for i, _, _ in e["faltan"]) or "-"
        s = ", ".join(f"{ings[a]['nombre']}->{ings[b]['nombre']}" for a, b in e["sustituidos"]) or "-"
        print(f"  {e['score']:5.1f}%  {e['receta']['nombre']:<32} faltan: {f} | sustitutos: {s}")


class Escenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.con = db.inicializar(os.path.join(cls.tmp, "t.db"))
        cls.cat = db.cargar_catalogo(cls.con)

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def d(self, *nombres):
        return despensa_por_nombre(self.con, nombres)

    def test_catalogo_tiene_40_recetas(self):
        self.assertEqual(len(self.cat[1]), 40)

    def test_1_despensa_completa_mexicana(self):
        desp = self.d("huevo", "jitomate", "cebolla", "chile", "tortilla de maiz")
        r = recomendar(self.cat, desp, "Mexicana", [])
        self.assertEqual(r["nivel"], 1)
        self.assertEqual(r["resultados"][0]["receta"]["nombre"], "Huevos a la mexicana")

    def test_2_adaptacion_cambia_antojo(self):
        desp = self.d("arroz", "huevo", "salsa de soya", "cebollin", "zanahoria")
        jap = recomendar(self.cat, desp, "Japonesa", [])
        chi = recomendar(self.cat, desp, "China", [])
        self.assertEqual(jap["resultados"][0]["receta"]["cocina"], "Japonesa")
        self.assertEqual(chi["resultados"][0]["receta"]["cocina"], "China")

    def test_3_sustituto(self):
        # sin crema pero con yogur: Pasta Alfredo usa yogur como sustituto
        desp = self.d("pasta", "yogur", "queso parmesano", "mantequilla")
        r = recomendar(self.cat, desp, "Italiana", [])
        alfredo = next(e for e in r["resultados"] if e["receta"]["nombre"] == "Pasta Alfredo")
        self.assertTrue(alfredo["sustituidos"])
        self.assertTrue(alfredo["cocinable"])

    def test_4_restriccion_vegetariano(self):
        desp = self.d("pollo", "tortilla de maiz", "cebolla", "huevo", "jitomate", "chile")
        r = recomendar(self.cat, desp, "Mexicana", ["Vegetariano"])
        for e in r["resultados"]:
            for i in e["receta"]["esenciales"]:
                self.assertNotIn("carne", self.cat[0][i]["tags"])
        nombres = [e["receta"]["nombre"] for e in r["resultados"]]
        self.assertNotIn("Tacos de pollo", nombres)

    def test_5_sin_gluten_descarta_pasta(self):
        desp = self.d("pasta", "salsa de tomate", "ajo")
        r = recomendar(self.cat, desp, "Italiana", ["Sin gluten"])
        nombres = [e["receta"]["nombre"] for e in r["resultados"]]
        self.assertNotIn("Spaghetti al pomodoro", nombres)

    def test_6_relajacion_a_otras_cocinas(self):
        # despensa tipicamente japonesa pero antojo mexicano -> debe ampliar
        desp = self.d("arroz", "salmon", "alga nori", "vinagre de arroz")
        r = recomendar(self.cat, desp, "Mexicana", [])
        self.assertIn(r["nivel"], (3, 4))
        self.assertTrue(r["resultados"])

    def test_7_despensa_vacia(self):
        r = recomendar(self.cat, set(), "Mexicana", [])
        self.assertEqual(r["nivel"], 0)


if __name__ == "__main__":
    tmp = tempfile.mkdtemp()
    con = db.inicializar(os.path.join(tmp, "demo.db"))
    cat = db.cargar_catalogo(con)
    esc = [
        ("Escenario 1: despensa completa, antojo Mexicana",
         ["huevo", "jitomate", "cebolla", "chile", "tortilla de maiz"], "Mexicana", []),
        ("Escenario 2: la despensa no alcanza para el antojo (Mexicana) con ingredientes japoneses",
         ["arroz", "salmon", "alga nori", "vinagre de arroz"], "Mexicana", []),
        ("Escenario 3: sustituto (sin crema, con yogur), Italiana",
         ["pasta", "yogur", "queso parmesano", "mantequilla"], "Italiana", []),
        ("Escenario 4: restriccion Vegetariano, Mexicana",
         ["pollo", "tortilla de maiz", "cebolla", "huevo", "jitomate", "chile"], "Mexicana", ["Vegetariano"]),
        ("Escenario 5: mismo inventario, cambia el antojo a Japonesa",
         ["arroz", "huevo", "salsa de soya", "cebollin", "zanahoria"], "Japonesa", []),
        ("Escenario 5b: mismo inventario, antojo China",
         ["arroz", "huevo", "salsa de soya", "cebollin", "zanahoria"], "China", []),
    ]
    for t, d, a, rs in esc:
        mostrar(t, cat, recomendar(cat, despensa_por_nombre(con, d), a, rs))
