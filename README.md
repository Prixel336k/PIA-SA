# Sistema Inteligente de Recomendación de Platillos — Sistemas Adaptativos

Aplicación de escritorio desarrollada en **Python**, **CustomTkinter**, **Pillow** y **SQLite** para la unidad de aprendizaje **Sistemas Adaptativos (UANL · FIME)**. El sistema recomienda platillos de distintas cocinas internacionales a partir de los ingredientes disponibles en la despensa del usuario, su preferencia culinaria del día y sus restricciones alimentarias.

---

## Características Principales

1. **Verificación de vigencia de la despensa:**
   - Registra la fecha de la última actualización del inventario y, al iniciar en un día posterior, consulta al usuario si conserva los mismos ingredientes o si desea actualizar aquellos que se hayan agotado.
2. **Interfaz estructurada en cinco vistas progresivas:**
   - **Vista 1 (Estado de la despensa):** Confirmación de la despensa registrada previamente, depuración rápida de insumos agotados o carga de inventario básico.
   - **Vista 2 (Preferencia culinaria):** Selección visual entre cinco tipos de cocina (*Mexicana, Italiana, Japonesa, India, China*) o modo de recomendación abierta (*Sorpréndeme*).
   - **Vista 3 (Restricciones alimentarias):** Configuración de filtros prioritarios (*Vegetariano, Sin gluten, Sin lácteos, Sin huevo, Sin mariscos, Sin soya, Sin frutos secos*).
   - **Vista 4 (Alacena completa):** Gestión de ingredientes organizada por categorías con búsqueda en tiempo real.
   - **Vista 5 (Platillos recomendados):** Lista ordenada por porcentaje de compatibilidad con fotografía del platillo, ingredientes disponibles, sustitutos sugeridos e insumos faltantes.
3. **Retroalimentación al preparar un platillo:**
   - En la vista de preparación paso a paso, la opción *Ya lo cociné* descuenta automáticamente de la despensa los ingredientes empleados y recalcula las recomendaciones.
4. **Módulo de administración del catálogo:**
   - **Gestión de recetas:** Alta, edición y baja de platillos, tiempos, dificultad, ingredientes esenciales/opcionales, pasos de preparación y fotografía asociada.
   - **Gestión de ingredientes:** Alta, edición y baja de insumos, clasificación por categoría, etiquetas de alérgenos y definición de sustitutos.

---

## Mecanismo de Adaptación

El motor evalúa el catálogo de 40 recetas en tiempo real mediante tres etapas:

1. **Filtrado prioritario de restricciones:**
   - Si una receta contiene como ingrediente esencial un insumo incompatible con las restricciones del usuario, la receta se descarta.
   - Si el insumo restringido es únicamente opcional, el sistema conserva la receta omitiendo dicho ingrediente y lo notifica en pantalla.
2. **Puntuación ponderada de compatibilidad (0% a 100%):**
   - Los ingredientes **esenciales** tienen un peso de `2` puntos y los **opcionales** un peso de `1` punto (los insumos básicos como agua, sal y aceite se asumen disponibles).
   - Un ingrediente presente en la despensa aporta el `100%` de su peso; si falta pero existe un **sustituto válido** en la despensa del usuario, aporta el `60%` de su peso.
3. **Relajación progresiva de criterios en 4 niveles:**
   - **Nivel 1:** Recetas de la cocina seleccionada con compatibilidad $\ge 60\%$ y la totalidad de sus ingredientes esenciales cubiertos.
   - **Nivel 2:** Si ninguna receta cumple el Nivel 1, reduce el umbral al $40\%$ dentro de la cocina seleccionada e indica los ingredientes esenciales faltantes.
   - **Nivel 3:** Si la despensa no alcanza el umbral en la cocina solicitada, amplía la búsqueda a otras cocinas del catálogo con recetas viables ($\ge 60\%$ y esenciales cubiertos).
   - **Nivel 4:** Cuando el inventario es insuficiente para cualquier cocina, presenta las opciones más cercanas del catálogo general junto con los ingredientes requeridos.

---

## Requisitos e Instalación

### Dependencias
- Python 3.10 o superior.
- Librerías listadas en `requirements.txt` (`customtkinter`, `pillow`).

### Instalación y ejecución desde terminal
```bash
python -m pip install -r requirements.txt
python src/main.py
```

En Windows también puede ejecutarse directamente mediante el archivo **`ejecutar.bat`**. La base de datos local `data/cocina.db` se genera e inicializa de forma automática en la primera ejecución.

---

## Ejecución de Pruebas

Para correr la batería de pruebas unitarias y visualizar en consola los escenarios de adaptación:
```bash
python -m unittest discover tests
python tests/test_escenarios.py
```

---

## Estructura del Repositorio

```text
Proyecto_SA/
├── data/
│   ├── schema.sql               # Esquema relacional de la base de datos SQLite
│   ├── seed_data.py             # Catálogo inicial (40 recetas, ingredientes y sustitutos)
│   └── fotos/                   # Fotografías de los platillos y tipos de cocina
├── src/
│   ├── main.py                  # Punto de entrada de la aplicación
│   ├── db.py                    # Acceso a datos y operaciones CRUD del catálogo
│   ├── logica/
│   │   ├── restricciones.py     # Filtrado por restricciones alimentarias y alergias
│   │   ├── puntuacion.py        # Cálculo de compatibilidad ponderada
│   │   ├── sustitutos.py        # Detección de ingredientes sustitutos disponibles
│   │   └── adaptacion.py        # Relajación progresiva (Niveles 1 a 4) y actualización
│   └── ui/
│       ├── app.py               # Ventana principal dividida en cinco vistas
│       ├── revision_despensa.py # Ventana de actualización rápida de inventario
│       ├── receta.py            # Vista de receta detallada y descuento de ingredientes
│       ├── admin.py             # Panel de administración de recetas e ingredientes
│       ├── imagenes.py          # Gestión y carga de fotografías del catálogo
│       └── estilo.py            # Definición de paleta de colores y etiquetas
├── tests/
│   └── test_escenarios.py       # Pruebas unitarias de los escenarios de adaptación
├── ejecutar.bat                 # Script de arranque para Windows
├── requirements.txt             # Dependencias del proyecto
└── README.md
```
