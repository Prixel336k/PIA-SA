"""Acceso a la base de datos SQLite (se crea sola la primera vez)."""
import os
import sqlite3
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "data"))
DB_PATH = os.path.join(BASE, "data", "cocina.db")
SCHEMA = os.path.join(BASE, "data", "schema.sql")


def conectar(path=None):
    con = sqlite3.connect(path or DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def inicializar(path=None):
    """Crea tablas y carga el catalogo si la BD esta vacia."""
    import seed_data
    con = conectar(path)
    with open(SCHEMA, encoding="utf-8") as f:
        con.executescript(f.read())
    if con.execute("SELECT COUNT(*) FROM recetas").fetchone()[0] == 0:
        for nombre, (cat, tags) in seed_data.INGREDIENTES.items():
            basico = 1 if cat == "Basicos" else 0
            con.execute("INSERT OR IGNORE INTO ingredientes(nombre,categoria,tags,basico) VALUES (?,?,?,?)",
                        (nombre, cat, tags, basico))
        ids = {r["nombre"]: r["id"] for r in con.execute("SELECT id,nombre FROM ingredientes")}
        for ing, subs in seed_data.SUSTITUTOS.items():
            for s in subs:
                if ing in ids and s in ids:
                    con.execute("INSERT OR IGNORE INTO sustitutos VALUES (?,?)", (ids[ing], ids[s]))
        for nom, coc, t, dif, esen, opc, pasos in seed_data.RECETAS:
            cur = con.execute("INSERT INTO recetas(nombre,cocina,tiempo,dificultad,pasos) VALUES (?,?,?,?,?)",
                              (nom, coc, t, dif, pasos))
            rid = cur.lastrowid
            for lista, es in ((esen, 1), (opc, 0)):
                for ing in [x.strip() for x in lista.split(",") if x.strip()]:
                    con.execute("INSERT INTO receta_ingredientes VALUES (?,?,?)", (rid, ids[ing], es))
        con.commit()
    return con


# ---------- consultas ----------
def ingredientes(con):
    return [dict(r) for r in con.execute(
        "SELECT * FROM ingredientes WHERE basico=0 ORDER BY categoria, nombre")]


def cocinas(con):
    return [r[0] for r in con.execute("SELECT DISTINCT cocina FROM recetas ORDER BY cocina")]


def cargar_catalogo(con):
    """Devuelve (ingredientes_por_id, recetas, sustitutos) en memoria para el motor."""
    ings = {r["id"]: dict(r) for r in con.execute("SELECT * FROM ingredientes")}
    recetas = {}
    for r in con.execute("SELECT * FROM recetas ORDER BY nombre"):
        recetas[r["id"]] = {**dict(r), "esenciales": [], "opcionales": []}
    for r in con.execute("SELECT * FROM receta_ingredientes"):
        clave = "esenciales" if r["esencial"] else "opcionales"
        recetas[r["receta_id"]][clave].append(r["ingrediente_id"])
    subs = {}
    for r in con.execute("SELECT * FROM sustitutos"):
        subs.setdefault(r["ingrediente_id"], []).append(r["sustituto_id"])
    return ings, recetas, subs


# ---------- estado del usuario ----------
def get_despensa(con):
    return {r[0] for r in con.execute("SELECT ingrediente_id FROM despensa")}


def set_despensa(con, ids, actualizar_fecha=True):
    from datetime import date
    con.execute("DELETE FROM despensa")
    con.executemany("INSERT INTO despensa VALUES (?)", [(i,) for i in ids])
    if actualizar_fecha:
        con.execute("INSERT OR REPLACE INTO config VALUES ('fecha_despensa', ?)", (date.today().isoformat(),))
    con.commit()


def get_config(con, clave, defecto=""):
    r = con.execute("SELECT valor FROM config WHERE clave=?", (clave,)).fetchone()
    return r[0] if r else defecto


def set_config(con, clave, valor):
    con.execute("INSERT OR REPLACE INTO config VALUES (?,?)", (clave, valor))
    con.commit()


# ---------- administrador (CRUD de recetas e ingredientes) ----------
def agregar_receta(con, nombre, cocina, tiempo, dificultad, esenciales, opcionales, pasos):
    ids = {r["nombre"]: r["id"] for r in con.execute("SELECT id,nombre FROM ingredientes")}
    faltan = [i for i in esenciales + opcionales if i not in ids]
    if faltan:
        raise ValueError("Ingredientes no registrados: " + ", ".join(faltan))
    cur = con.execute("INSERT INTO recetas(nombre,cocina,tiempo,dificultad,pasos) VALUES (?,?,?,?,?)",
                      (nombre, cocina, tiempo, dificultad, pasos))
    for lista, es in ((esenciales, 1), (opcionales, 0)):
        for i in lista:
            con.execute("INSERT OR IGNORE INTO receta_ingredientes VALUES (?,?,?)", (cur.lastrowid, ids[i], es))
    con.commit()
    return cur.lastrowid


def editar_receta(con, rid, nombre, cocina, tiempo, dificultad, esenciales, opcionales, pasos):
    ids = {r["nombre"]: r["id"] for r in con.execute("SELECT id,nombre FROM ingredientes")}
    faltan = [i for i in esenciales + opcionales if i not in ids]
    if faltan:
        raise ValueError("Ingredientes no registrados: " + ", ".join(faltan))
    con.execute(
        "UPDATE recetas SET nombre=?, cocina=?, tiempo=?, dificultad=?, pasos=? WHERE id=?",
        (nombre, cocina, tiempo, dificultad, pasos, rid)
    )
    con.execute("DELETE FROM receta_ingredientes WHERE receta_id=?", (rid,))
    for lista, es in ((esenciales, 1), (opcionales, 0)):
        for i in lista:
            con.execute("INSERT OR IGNORE INTO receta_ingredientes VALUES (?,?,?)", (rid, ids[i], es))
    con.commit()


def borrar_receta(con, rid):
    con.execute("DELETE FROM recetas WHERE id=?", (rid,))
    con.commit()


def agregar_ingrediente(con, nombre, categoria, tags="", sustitutos=None):
    nombre = nombre.strip().lower()
    if not nombre:
        raise ValueError("Escribe el nombre del ingrediente.")
    existente = con.execute("SELECT id FROM ingredientes WHERE nombre=?", (nombre,)).fetchone()
    if existente:
        iid = existente["id"]
        con.execute("UPDATE ingredientes SET categoria=?, tags=? WHERE id=?", (categoria, tags, iid))
    else:
        cur = con.execute(
            "INSERT INTO ingredientes(nombre,categoria,tags,basico) VALUES (?,?,?,0)",
            (nombre, categoria, tags)
        )
        iid = cur.lastrowid

    if sustitutos is not None:
        con.execute("DELETE FROM sustitutos WHERE ingrediente_id=?", (iid,))
        ids = {r["nombre"]: r["id"] for r in con.execute("SELECT id,nombre FROM ingredientes")}
        for s in sustitutos:
            s_nom = s.strip().lower()
            if s_nom in ids and ids[s_nom] != iid:
                con.execute("INSERT OR IGNORE INTO sustitutos VALUES (?,?)", (iid, ids[s_nom]))
    con.commit()
    return iid


def borrar_ingrediente(con, iid):
    con.execute("DELETE FROM receta_ingredientes WHERE ingrediente_id=?", (iid,))
    con.execute("DELETE FROM sustitutos WHERE ingrediente_id=? OR sustituto_id=?", (iid, iid))
    con.execute("DELETE FROM despensa WHERE ingrediente_id=?", (iid,))
    con.execute("DELETE FROM ingredientes WHERE id=?", (iid,))
    con.commit()
