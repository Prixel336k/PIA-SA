# Recomendador de platillos – Sistema adaptativo

Aplicación de escritorio (Python + CustomTkinter + SQLite) que recomienda platillos según los
ingredientes disponibles, el antojo del día (tipo de cocina) y las restricciones alimentarias.

## Instalación y uso
```
python -m pip install customtkinter
python src/main.py
```
La base de datos `data/cocina.db` se crea sola la primera vez con 40 recetas.

## Pruebas
```
python -m unittest discover tests
python tests/test_escenarios.py      # imprime los escenarios de la Evidencia 3
```

## Estructura
```
data/        schema.sql, seed_data.py (catálogo), cocina.db (se genera)
src/         main.py, db.py
  logica/    restricciones, puntuacion, sustitutos, adaptacion (núcleo adaptativo)
  ui/        app, receta, admin
tests/       escenarios de prueba
```

## Cómo adapta (resumen)
Puntuación ponderada (esencial 2, opcional 1, sustituto 60 %) + relajación progresiva en 4 niveles
(umbral 60 % → 40 % → otras cocinas → mejores opciones con lista de compras). Se recalcula con
cualquier cambio de despensa, antojo o restricciones, y al marcar «Ya lo cociné».
