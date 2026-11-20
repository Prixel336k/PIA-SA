"""Administrador del catálogo: agregar, editar y borrar recetas e ingredientes."""
from tkinter import filedialog, messagebox
import customtkinter as ctk

import db
from ui.imagenes import guardar_foto_personalizada, limpiar_cache_memoria
from ui.estilo import (
    BG_CREMA, CARD_BLANCO, TERRACOTA, TERRACOTA_HOVER, VERDE_COCINA,
    VERDE_CLARO, GRIS_CHIP, GRIS_TEXTO, etiqueta_ing
)

CATEGORIAS_ING = [
    "Verduras y frutas",
    "Carnes",
    "Lacteos y huevo",
    "Cereales y masas",
    "Legumbres",
    "Salsas y especias",
    "Pescados y mariscos",
]

TAGS_DISPONIBLES = [
    ("carne", "🥩 Carne"),
    ("pescado", "🐟 Pescado"),
    ("marisco", "🦐 Marisco"),
    ("lacteo", "🥛 Lácteo"),
    ("huevo", "🥚 Huevo"),
    ("gluten", "🌾 Gluten"),
    ("soya", "🍶 Soya"),
    ("nueces", "🥜 Frutos secos"),
]


class VentanaAdmin(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("⚙️ Administrador del Catálogo (Recetas e Ingredientes)")
        self.geometry("1040x700")
        self.minsize(920, 620)
        self.configure(fg_color=BG_CREMA)
        self.after(150, self.focus)

        self.receta_editando_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Barra superior para alternar entre Recetas e Ingredientes
        top = ctk.CTkFrame(self, fg_color=TERRACOTA, corner_radius=0, height=58)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top, text="⚙️ Administración del Catálogo",
            font=("Segoe UI", 20, "bold"), text_color="white"
        ).grid(row=0, column=0, sticky="w", padx=18, pady=12)

        selector = ctk.CTkFrame(top, fg_color="transparent")
        selector.grid(row=0, column=1, sticky="e", padx=18, pady=10)

        self.btn_tab_recetas = ctk.CTkButton(
            selector, text="🍲 Recetas (Agregar / Editar / Borrar)",
            height=36, corner_radius=8, font=("Segoe UI", 13, "bold"),
            command=lambda: self.mostrar_seccion("recetas")
        )
        self.btn_tab_recetas.pack(side="left", padx=4)

        self.btn_tab_ings = ctk.CTkButton(
            selector, text="🥬 Ingredientes (Agregar / Editar / Borrar)",
            height=36, corner_radius=8, font=("Segoe UI", 13, "bold"),
            command=lambda: self.mostrar_seccion("ingredientes")
        )
        self.btn_tab_ings.pack(side="left", padx=4)

        # Contenedor central
        self.contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor.grid(row=1, column=0, sticky="nsew", padx=14, pady=12)
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.contenedor.grid_rowconfigure(0, weight=1)

        self._crear_vista_recetas()
        self._crear_vista_ingredientes()
        self.mostrar_seccion("recetas")

    def mostrar_seccion(self, cual):
        if cual == "recetas":
            self.btn_tab_recetas.configure(fg_color=VERDE_COCINA, hover_color="#1B5E20", text_color="white")
            self.btn_tab_ings.configure(fg_color="#5D4037", hover_color="#3E2723", text_color="white")
            self.vista_ings.grid_forget()
            self._pintar_recetas()
            self.vista_recetas.grid(row=0, column=0, sticky="nsew")
        else:
            self.btn_tab_ings.configure(fg_color=VERDE_COCINA, hover_color="#1B5E20", text_color="white")
            self.btn_tab_recetas.configure(fg_color="#5D4037", hover_color="#3E2723", text_color="white")
            self.vista_recetas.grid_forget()
            self._pintar_ingredientes()
            self.vista_ings.grid(row=0, column=0, sticky="nsew")

    # =========================================================================
    # SECCIÓN 1: ADMINISTRAR RECETAS (AGREGAR, EDITAR Y BORRAR)
    # =========================================================================
    def _crear_vista_recetas(self):
        self.vista_recetas = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        self.vista_recetas.grid_columnconfigure(0, weight=4)
        self.vista_recetas.grid_columnconfigure(1, weight=6)
        self.vista_recetas.grid_rowconfigure(0, weight=1)

        # Panel izquierdo: Lista de recetas con Editar y Borrar
        izq = ctk.CTkFrame(self.vista_recetas, fg_color=CARD_BLANCO, corner_radius=12, border_width=1, border_color="#E0D6C8")
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        izq.grid_columnconfigure(0, weight=1)
        izq.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            izq, text="📋 Recetas en el catálogo",
            font=("Segoe UI", 16, "bold"), text_color="#3E2723"
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))

        self.var_busq_rec = ctk.StringVar()
        self.var_busq_rec.trace_add("write", lambda *_: self._pintar_recetas())
        ctk.CTkEntry(
            izq, textvariable=self.var_busq_rec,
            placeholder_text="🔍 Buscar receta por nombre o cocina..."
        ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))

        self.lista_recetas = ctk.CTkScrollableFrame(izq, fg_color="#FAF6F0", corner_radius=10)
        self.lista_recetas.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))

        # Panel derecho: Formulario de Agregar / Editar receta
        f = ctk.CTkFrame(self.vista_recetas, fg_color=CARD_BLANCO, corner_radius=12, border_width=1, border_color="#E0D6C8")
        f.grid(row=0, column=1, sticky="nsew")
        f.grid_columnconfigure(1, weight=1)
        f.grid_rowconfigure(8, weight=1)

        cab_f = ctk.CTkFrame(f, fg_color="transparent")
        cab_f.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(12, 6))
        self.lbl_modo_receta = ctk.CTkLabel(
            cab_f, text="➕ Agregar nueva receta",
            font=("Segoe UI", 17, "bold"), text_color=TERRACOTA
        )
        self.lbl_modo_receta.pack(side="left")

        ctk.CTkButton(
            cab_f, text="➕ Limpiar (Nueva receta)", width=160, height=30,
            fg_color="#6D4C41", hover_color="#4E342E", font=("Segoe UI", 12, "bold"),
            command=self.limpiar_form_receta
        ).pack(side="right")

        self.e_nombre = self._campo(f, 1, "Nombre del platillo:")
        self.e_cocina = self._campo(f, 2, "Cocina (ej. Mexicana, Italiana):")
        self.e_tiempo = self._campo(f, 3, "Tiempo aproximado (minutos):")

        ctk.CTkLabel(f, text="Dificultad:", font=("Segoe UI", 13)).grid(row=4, column=0, sticky="w", padx=14, pady=4)
        self.m_dif = ctk.CTkOptionMenu(f, values=["Facil", "Media", "Dificil"], fg_color=TERRACOTA, button_color=TERRACOTA_HOVER)
        self.m_dif.grid(row=4, column=1, sticky="w", padx=14, pady=4)

        self.e_esen = self._campo(f, 5, "Ingredientes esenciales\n(separados por coma):")
        self.e_opc = self._campo(f, 6, "Ingredientes opcionales\n(separados por coma):")

        # Campo opcional para fotografía del platillo
        ctk.CTkLabel(f, text="Foto (URL o archivo opcional):", font=("Segoe UI", 13)).grid(row=7, column=0, sticky="w", padx=14, pady=4)
        marco_foto = ctk.CTkFrame(f, fg_color="transparent")
        marco_foto.grid(row=7, column=1, sticky="ew", padx=14, pady=4)
        marco_foto.grid_columnconfigure(0, weight=1)
        self.e_foto = ctk.CTkEntry(marco_foto, placeholder_text="Opcional: pega un link https://... o elige una imagen de tu PC")
        self.e_foto.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(
            marco_foto, text="📂 Buscar...", width=90,
            fg_color="#6D4C41", hover_color="#4E342E",
            command=self._elegir_archivo_foto
        ).grid(row=0, column=1)

        ctk.CTkLabel(f, text="Pasos de preparación\n(uno por línea):", justify="left", font=("Segoe UI", 13)).grid(
            row=8, column=0, sticky="nw", padx=14, pady=6
        )
        self.t_pasos = ctk.CTkTextbox(f, height=130, fg_color="#FAF6F0", border_width=1, border_color="#D7CCC8")
        self.t_pasos.grid(row=8, column=1, sticky="nsew", padx=14, pady=6)

        self.btn_guardar_receta = ctk.CTkButton(
            f, text="💾 Guardar nueva receta", height=42,
            fg_color=VERDE_COCINA, hover_color="#1B5E20",
            font=("Segoe UI", 14, "bold"), command=self.guardar_receta
        )
        self.btn_guardar_receta.grid(row=9, column=0, columnspan=2, sticky="ew", padx=14, pady=12)

    def _campo(self, parent, fila, texto):
        ctk.CTkLabel(parent, text=texto, justify="left", font=("Segoe UI", 13)).grid(
            row=fila, column=0, sticky="w", padx=14, pady=4
        )
        e = ctk.CTkEntry(parent)
        e.grid(row=fila, column=1, sticky="ew", padx=14, pady=4)
        return e

    def _elegir_archivo_foto(self):
        ruta = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar fotografía del platillo",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp")]
        )
        if ruta:
            self.e_foto.delete(0, "end")
            self.e_foto.insert(0, ruta)

    def _pintar_recetas(self):
        for w in self.lista_recetas.winfo_children():
            w.destroy()
        filtro = self.var_busq_rec.get().strip().lower()
        recetas = sorted(self.app.catalogo[1].values(), key=lambda x: (x["cocina"], x["nombre"]))
        for r in recetas:
            if filtro and filtro not in r["nombre"].lower() and filtro not in r["cocina"].lower():
                continue
            fila = ctk.CTkFrame(self.lista_recetas, fg_color=CARD_BLANCO, corner_radius=8)
            fila.pack(fill="x", pady=3, padx=2)
            ctk.CTkLabel(
                fila, text=f"[{r['cocina'][:3]}] {r['nombre']}",
                anchor="w", font=("Segoe UI", 12, "bold"), text_color="#3E2723"
            ).pack(side="left", fill="x", expand=True, padx=8, pady=6)

            ctk.CTkButton(
                fila, text="🗑️", width=34, height=28,
                fg_color="#C62828", hover_color="#8E0000",
                command=lambda rid=r["id"], n=r["nombre"]: self.borrar_receta(rid, n)
            ).pack(side="right", padx=(2, 6), pady=4)

            ctk.CTkButton(
                fila, text="✏️ Editar", width=72, height=28,
                fg_color=TERRACOTA, hover_color=TERRACOTA_HOVER,
                font=("Segoe UI", 11, "bold"),
                command=lambda rec=r: self.cargar_receta_en_form(rec)
            ).pack(side="right", padx=2, pady=4)

    def cargar_receta_en_form(self, r):
        """Carga los datos de la receta seleccionada en el formulario para editarla."""
        ings = self.app.catalogo[0]
        self.receta_editando_id = r["id"]
        self.lbl_modo_receta.configure(text=f"✏️ Editando: {r['nombre']}", text_color="#1565C0")
        self.btn_guardar_receta.configure(text="💾 Guardar cambios en la receta", fg_color="#1565C0", hover_color="#0D47A1")

        for entry, val in (
            (self.e_nombre, r["nombre"]),
            (self.e_cocina, r["cocina"]),
            (self.e_tiempo, str(r["tiempo"])),
            (self.e_esen, ", ".join(ings[i]["nombre"] for i in r["esenciales"])),
            (self.e_opc, ", ".join(ings[i]["nombre"] for i in r["opcionales"])),
            (self.e_foto, ""),
        ):
            entry.delete(0, "end")
            entry.insert(0, val)

        self.m_dif.set(r["dificultad"])
        self.t_pasos.delete("1.0", "end")
        self.t_pasos.insert("1.0", "\n".join(r["pasos"].split("|")))

    def limpiar_form_receta(self):
        self.receta_editando_id = None
        self.lbl_modo_receta.configure(text="➕ Agregar nueva receta", text_color=TERRACOTA)
        self.btn_guardar_receta.configure(text="💾 Guardar nueva receta", fg_color=VERDE_COCINA, hover_color="#1B5E20")
        for e in (self.e_nombre, self.e_cocina, self.e_tiempo, self.e_esen, self.e_opc, self.e_foto):
            e.delete(0, "end")
        self.t_pasos.delete("1.0", "end")

    def borrar_receta(self, rid, nombre):
        if messagebox.askyesno("Borrar receta", f"¿Seguro que deseas borrar '{nombre}'?", parent=self):
            db.borrar_receta(self.app.con, rid)
            if self.receta_editando_id == rid:
                self.limpiar_form_receta()
            self.app.recargar_catalogo()
            self._pintar_recetas()

    def guardar_receta(self):
        try:
            nombre = self.e_nombre.get().strip()
            cocina = self.e_cocina.get().strip().capitalize()
            tiempo = int(self.e_tiempo.get().strip())
            esen = [x.strip().lower() for x in self.e_esen.get().split(",") if x.strip()]
            opc = [x.strip().lower() for x in self.e_opc.get().split(",") if x.strip()]
            pasos = "|".join(p.strip() for p in self.t_pasos.get("1.0", "end").splitlines() if p.strip())
            if not (nombre and cocina and esen and pasos):
                raise ValueError("Completa nombre, cocina, ingredientes esenciales y pasos.")

            if self.receta_editando_id is not None:
                db.editar_receta(
                    self.app.con, self.receta_editando_id,
                    nombre, cocina, tiempo, self.m_dif.get(), esen, opc, pasos
                )
                msg = f"Receta '{nombre}' actualizada correctamente."
            else:
                db.agregar_receta(
                    self.app.con, nombre, cocina, tiempo, self.m_dif.get(), esen, opc, pasos
                )
                msg = f"Nueva receta '{nombre}' agregada al catálogo."

            foto_origen = self.e_foto.get().strip()
            if foto_origen:
                guardar_foto_personalizada(nombre, foto_origen)
            limpiar_cache_memoria()
        except Exception as ex:
            messagebox.showerror(
                "No se pudo guardar",
                f"{ex}\n\nTip: Si tu receta usa un ingrediente nuevo, agrégalo primero en la pestaña «🥬 Ingredientes».",
                parent=self
            )
            return

        self.app.recargar_catalogo()
        self._pintar_recetas()
        self.limpiar_form_receta()
        messagebox.showinfo("Listo", msg, parent=self)

    # =========================================================================
    # SECCIÓN 2: ADMINISTRAR INGREDIENTES (AGREGAR, EDITAR Y BORRAR)
    # =========================================================================
    def _crear_vista_ingredientes(self):
        self.vista_ings = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        self.vista_ings.grid_columnconfigure(0, weight=5)
        self.vista_ings.grid_columnconfigure(1, weight=5)
        self.vista_ings.grid_rowconfigure(0, weight=1)

        # Panel izquierdo: Lista de ingredientes registrados
        izq = ctk.CTkFrame(self.vista_ings, fg_color=CARD_BLANCO, corner_radius=12, border_width=1, border_color="#E0D6C8")
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        izq.grid_columnconfigure(0, weight=1)
        izq.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            izq, text="🥬 Ingredientes en el sistema",
            font=("Segoe UI", 16, "bold"), text_color="#3E2723"
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))

        self.var_busq_ing = ctk.StringVar()
        self.var_busq_ing.trace_add("write", lambda *_: self._pintar_ingredientes())
        ctk.CTkEntry(
            izq, textvariable=self.var_busq_ing,
            placeholder_text="🔍 Buscar ingrediente (ej. pollo, nopales, plátano)..."
        ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))

        self.lista_ings_frame = ctk.CTkScrollableFrame(izq, fg_color="#FAF6F0", corner_radius=10)
        self.lista_ings_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))

        # Panel derecho: Formulario para agregar o editar un ingrediente
        der = ctk.CTkFrame(self.vista_ings, fg_color=CARD_BLANCO, corner_radius=12, border_width=1, border_color="#E0D6C8")
        der.grid(row=0, column=1, sticky="nsew")
        der.grid_columnconfigure(1, weight=1)

        cab = ctk.CTkFrame(der, fg_color="transparent")
        cab.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(14, 8))
        self.lbl_modo_ing = ctk.CTkLabel(
            cab, text="➕ Agregar o editar ingrediente",
            font=("Segoe UI", 17, "bold"), text_color=VERDE_COCINA
        )
        self.lbl_modo_ing.pack(side="left")

        ctk.CTkButton(
            cab, text="➕ Limpiar formulario", width=145, height=30,
            fg_color="#6D4C41", hover_color="#4E342E", font=("Segoe UI", 12, "bold"),
            command=self.limpiar_form_ingrediente
        ).pack(side="right")

        self.e_ing_nombre = self._campo(der, 1, "Nombre del ingrediente\n(ej. platano, nopales, elote):")

        ctk.CTkLabel(der, text="Categoría en la alacena:", font=("Segoe UI", 13)).grid(
            row=2, column=0, sticky="w", padx=14, pady=8
        )
        self.m_ing_cat = ctk.CTkOptionMenu(
            der, values=CATEGORIAS_ING, fg_color=TERRACOTA, button_color=TERRACOTA_HOVER
        )
        self.m_ing_cat.grid(row=2, column=1, sticky="ew", padx=14, pady=8)

        ctk.CTkLabel(
            der,
            text="Etiquetas de alergia/restricción\n(marca si contiene alguno):",
            justify="left", font=("Segoe UI", 13)
        ).grid(row=3, column=0, sticky="nw", padx=14, pady=8)

        marco_tags = ctk.CTkFrame(der, fg_color="#FAF6F0", corner_radius=10)
        marco_tags.grid(row=3, column=1, sticky="ew", padx=14, pady=8)
        for c in range(2):
            marco_tags.grid_columnconfigure(c, weight=1)

        self.vars_tag_ing = {}
        for idx, (clave_tag, etiqueta) in enumerate(TAGS_DISPONIBLES):
            v = ctk.BooleanVar(value=False)
            ctk.CTkCheckBox(
                marco_tags, text=etiqueta, variable=v,
                font=("Segoe UI", 12), fg_color=TERRACOTA, hover_color=TERRACOTA_HOVER,
                checkbox_width=18, checkbox_height=18
            ).grid(row=idx // 2, column=idx % 2, sticky="w", padx=10, pady=5)
            self.vars_tag_ing[clave_tag] = v

        self.e_ing_subs = self._campo(
            der, 4, "Posibles sustitutos\n(opcional, separados por coma):"
        )

        ctk.CTkLabel(
            der,
            text="💡 Nota: Al guardar un ingrediente nuevo, aparecerá inmediatamente en «Mi Alacena»\n"
                 "y ya podrás usarlo al crear o editar cualquier receta.",
            font=("Segoe UI", 12), text_color="#5D4037", justify="left"
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 6))

        ctk.CTkButton(
            der, text="💾 Guardar ingrediente en el catálogo", height=44,
            fg_color=VERDE_COCINA, hover_color="#1B5E20",
            font=("Segoe UI", 14, "bold"), command=self.guardar_ingrediente
        ).grid(row=6, column=0, columnspan=2, sticky="ew", padx=16, pady=14)

    def _pintar_ingredientes(self):
        for w in self.lista_ings_frame.winfo_children():
            w.destroy()
        filtro = self.var_busq_ing.get().strip().lower()
        ings_catalogo, _, subs_map = self.app.catalogo
        for ing in db.ingredientes(self.app.con):
            if filtro and filtro not in ing["nombre"].lower() and filtro not in ing["categoria"].lower():
                continue
            fila = ctk.CTkFrame(self.lista_ings_frame, fg_color=CARD_BLANCO, corner_radius=8)
            fila.pack(fill="x", pady=3, padx=2)

            tags_txt = f"  ({ing['tags']})" if ing["tags"] else ""
            ctk.CTkLabel(
                fila,
                text=f"{etiqueta_ing(ing['nombre'])}  •  {ing['categoria']}{tags_txt}",
                anchor="w", font=("Segoe UI", 12, "bold"), text_color="#3E2723"
            ).pack(side="left", fill="x", expand=True, padx=8, pady=6)

            ctk.CTkButton(
                fila, text="🗑️", width=34, height=28,
                fg_color="#C62828", hover_color="#8E0000",
                command=lambda iid=ing["id"], n=ing["nombre"]: self.borrar_ingrediente(iid, n)
            ).pack(side="right", padx=(2, 6), pady=4)

            subs_nombres = [ings_catalogo[s]["nombre"] for s in subs_map.get(ing["id"], []) if s in ings_catalogo]
            ctk.CTkButton(
                fila, text="✏️ Editar", width=72, height=28,
                fg_color=TERRACOTA, hover_color=TERRACOTA_HOVER,
                font=("Segoe UI", 11, "bold"),
                command=lambda item=ing, sn=subs_nombres: self.cargar_ingrediente_en_form(item, sn)
            ).pack(side="right", padx=2, pady=4)

    def cargar_ingrediente_en_form(self, ing, subs_nombres):
        self.lbl_modo_ing.configure(text=f"✏️ Editando ingrediente: {ing['nombre']}", text_color="#1565C0")
        self.e_ing_nombre.delete(0, "end")
        self.e_ing_nombre.insert(0, ing["nombre"])
        if ing["categoria"] in CATEGORIAS_ING:
            self.m_ing_cat.set(ing["categoria"])
        tags_activos = {t.strip() for t in ing["tags"].split(",") if t.strip()}
        for k, v in self.vars_tag_ing.items():
            v.set(k in tags_activos)
        self.e_ing_subs.delete(0, "end")
        self.e_ing_subs.insert(0, ", ".join(subs_nombres))

    def limpiar_form_ingrediente(self):
        self.lbl_modo_ing.configure(text="➕ Agregar o editar ingrediente", text_color=VERDE_COCINA)
        self.e_ing_nombre.delete(0, "end")
        self.e_ing_subs.delete(0, "end")
        for v in self.vars_tag_ing.values():
            v.set(False)

    def guardar_ingrediente(self):
        try:
            nombre = self.e_ing_nombre.get().strip().lower()
            categoria = self.m_ing_cat.get()
            tags = ",".join(k for k, v in self.vars_tag_ing.items() if v.get())
            subs = [s.strip().lower() for s in self.e_ing_subs.get().split(",") if s.strip()]
            db.agregar_ingrediente(self.app.con, nombre, categoria, tags, subs)
        except Exception as ex:
            messagebox.showerror("Error al guardar ingrediente", str(ex), parent=self)
            return

        self.app.recargar_catalogo()
        self._pintar_ingredientes()
        self.limpiar_form_ingrediente()
        messagebox.showinfo("Listo", f"Ingrediente '{nombre}' guardado en el catálogo.", parent=self)

    def borrar_ingrediente(self, iid, nombre):
        if messagebox.askyesno("Borrar ingrediente", f"¿Seguro que deseas borrar '{nombre}'?", parent=self):
            db.borrar_ingrediente(self.app.con, iid)
            self.app.recargar_catalogo()
            self._pintar_ingredientes()
