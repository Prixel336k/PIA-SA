PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ingredientes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT NOT NULL UNIQUE,
    categoria TEXT NOT NULL,
    tags      TEXT NOT NULL DEFAULT '',   -- carne,pescado,marisco,lacteo,huevo,gluten,soya,nueces
    basico    INTEGER NOT NULL DEFAULT 0  -- 1 = se asume que siempre hay (sal, aceite...)
);

CREATE TABLE IF NOT EXISTS recetas (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT NOT NULL UNIQUE,
    cocina    TEXT NOT NULL,
    tiempo    INTEGER NOT NULL,           -- minutos (solo informativo)
    dificultad TEXT NOT NULL,             -- Facil / Media / Dificil (solo informativo)
    pasos     TEXT NOT NULL               -- pasos separados por '|'
);

CREATE TABLE IF NOT EXISTS receta_ingredientes (
    receta_id      INTEGER NOT NULL REFERENCES recetas(id) ON DELETE CASCADE,
    ingrediente_id INTEGER NOT NULL REFERENCES ingredientes(id),
    esencial       INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (receta_id, ingrediente_id)
);

CREATE TABLE IF NOT EXISTS sustitutos (
    ingrediente_id INTEGER NOT NULL REFERENCES ingredientes(id),
    sustituto_id   INTEGER NOT NULL REFERENCES ingredientes(id),
    PRIMARY KEY (ingrediente_id, sustituto_id)
);

-- Estado del usuario (sin login: un solo perfil local)
CREATE TABLE IF NOT EXISTS despensa (
    ingrediente_id INTEGER PRIMARY KEY REFERENCES ingredientes(id)
);

CREATE TABLE IF NOT EXISTS config (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);
