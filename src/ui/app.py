"""Ventana principal: despensa + antojo + restricciones -> recomendaciones en vivo."""
import customtkinter as ctk

import db
from logica.adaptacion import recomendar, SORPRENDEME
from logica.restricciones import RESTRICCIONES
from ui.receta import VentanaReceta
from ui.admin import VentanaAdmin

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

COLORES_NIVEL = {0: "#9e9e9e", 1: "#2e7d32", 2: "#f9a825", 3: "#ef6c00", 4: "#c62828"}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Recomendador de platillos - Sistema adaptativo")
        self.geometry("1180x720")
        self.minsize(1000, 600)

        self.con = db.inicializar()
        self.catalogo = db.cargar_catalogo(self.con)
        self.lista_ings = db.ingredientes(self.con)
        despensa = db.get_despensa(self.con)
        self.vars_ing = {i["id"]: ctk.BooleanVar(value=i["id"] in despensa) for i in self.lista_ings}

        guardadas = set(filter(None, db.get_config(self.con, "restricciones").split(";")))
        self.vars_res = {r: ctk.BooleanVar(value=r in guardadas) for r in RESTRICCIONES}
        self.var_antojo = ctk.StringVar(value=db.get_config(self.con, "antojo", SORPRENDEME))
        self.var_buscar = ctk.StringVar()
        self.var_buscar.trace_add("write", lambda *_: self._pintar_ingredientes())

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._panel_izquierdo()
        self._panel_derecho()
        self._pintar_ingredientes()
        self.refrescar()

    # ---------------- paneles ----------------
    def _panel_izquierdo(self):
        izq = ctk.CTkFrame(self, width=340)
        izq.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        izq.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(izq, text="1. ¿Qué se te antoja?", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 2))
        opciones = [SORPRENDEME] + db.cocinas(self.con)
        ctk.CTkOptionMenu(izq, values=opciones, variable=self.var_antojo,
                          command=lambda _: self.refrescar()).grid(row=1, column=0, sticky="ew", padx=10)

        ctk.CTkLabel(izq, text="2. Restricciones", font=("Segoe UI", 14, "bold")).grid(
            row=2, column=0, sticky="w", padx=10, pady=(10, 2))
        marco = ctk.CTkFrame(izq, fg_color="transparent")
        marco.grid(row=3, column=0, sticky="ew", padx=10)
        for n, (r, v) in enumerate(self.vars_res.items()):
            ctk.CTkCheckBox(marco, text=r, variable=v, command=self.refrescar,
                            checkbox_width=18, checkbox_height=18).grid(row=n // 2, column=n % 2, sticky="w", pady=2, padx=(0, 8))

        ctk.CTkLabel(izq, text="3. Tu despensa", font=("Segoe UI", 14, "bold")).grid(
            row=4, column=0, sticky="w", padx=10, pady=(10, 2))
        self.scroll_ing = ctk.CTkScrollableFrame(izq)
        self.scroll_ing.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0, 5))
        ctk.CTkEntry(izq, textvariable=self.var_buscar, placeholder_text="Buscar ingrediente...").grid(
            row=6, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.lbl_cuenta = ctk.CTkLabel(izq, text="")
        self.lbl_cuenta.grid(row=7, column=0, sticky="w", padx=10)
        botones = ctk.CTkFrame(izq, fg_color="transparent")
        botones.grid(row=8, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkButton(botones, text="Vaciar despensa", fg_color="#757575", hover_color="#616161",
                      command=self.vaciar).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ctk.CTkButton(botones, text="Administrar recetas", command=self.abrir_admin).pack(
            side="left", expand=True, fill="x", padx=(4, 0))

    def _panel_derecho(self):
        der = ctk.CTkFrame(self)
        der.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        der.grid_columnconfigure(0, weight=1)
        der.grid_rowconfigure(1, weight=1)
        self.banner = ctk.CTkLabel(der, text="", wraplength=700, justify="left",
                                   text_color="white", corner_radius=8, anchor="w", padx=12, pady=10)
        self.banner.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.scroll_res = ctk.CTkScrollableFrame(der, label_text="Platillos recomendados")
        self.scroll_res.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_res.grid_columnconfigure(0, weight=1)

    # ---------------- ingredientes ----------------
    def _pintar_ingredientes(self):
        for w in self.scroll_ing.winfo_children():
            w.destroy()
        filtro = self.var_buscar.get().strip().lower()
        categoria = None
        for ing in self.lista_ings:
            if filtro and filtro not in ing["nombre"]:
                continue
            if ing["categoria"] != categoria:
                categoria = ing["categoria"]
                ctk.CTkLabel(self.scroll_ing, text=categoria, font=("Segoe UI", 12, "bold"),
                             text_color="#2e7d32").pack(anchor="w", pady=(8, 0))
            ctk.CTkCheckBox(self.scroll_ing, text=ing["nombre"], variable=self.vars_ing[ing["id"]],
                            command=self.refrescar, checkbox_width=18, checkbox_height=18).pack(anchor="w", pady=1)

    def despensa_actual(self):
        return {i for i, v in self.vars_ing.items() if v.get()}

    def restricciones_actuales(self):
        return [r for r, v in self.vars_res.items() if v.get()]

    def vaciar(self):
        for v in self.vars_ing.values():
            v.set(False)
        self.refrescar()

    # ---------------- ADAPTACION: recalcula ante cualquier cambio ----------------
    def refrescar(self):
        despensa = self.despensa_actual()
        restricciones = self.restricciones_actuales()
        db.set_despensa(self.con, despensa)
        db.set_config(self.con, "antojo", self.var_antojo.get())
        db.set_config(self.con, "restricciones", ";".join(restricciones))
        self.lbl_cuenta.configure(text=f"{len(despensa)} ingredientes seleccionados")

        res = recomendar(self.catalogo, despensa, self.var_antojo.get(), restricciones)
        self.resultado = res
        extra = f"\nRecetas descartadas por tus restricciones: {res['descartadas']}" if res["descartadas"] else ""
        self.banner.configure(text=res["mensaje"] + extra, fg_color=COLORES_NIVEL[res["nivel"]])

        for w in self.scroll_res.winfo_children():
            w.destroy()
        for n, e in enumerate(res["resultados"]):
            self._tarjeta(n, e)

    def _tarjeta(self, fila, e):
        ings = self.catalogo[0]
        r = e["receta"]
        nom = lambda i: ings[i]["nombre"]
        card = ctk.CTkFrame(self.scroll_res, border_width=1, border_color="#c8c8c8")
        card.grid(row=fila, column=0, sticky="ew", pady=5, padx=4)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=r["nombre"], font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, sticky="w", padx=12, pady=(8, 0))
        ctk.CTkLabel(card, text=f"{r['cocina']}  •  {r['tiempo']} min  •  {r['dificultad']}",
                     text_color="#616161").grid(row=1, column=0, sticky="w", padx=12)
        barra = ctk.CTkProgressBar(card, progress_color="#2e7d32" if e["cocinable"] else "#ef6c00")
        barra.set(e["score"] / 100)
        barra.grid(row=2, column=0, sticky="ew", padx=12, pady=(6, 0))
        ctk.CTkLabel(card, text=f"Compatibilidad {e['score']:.0f}%" +
                     ("  ✔ Puedes prepararlo" if e["cocinable"] else "  ✖ Te faltan ingredientes esenciales")).grid(
            row=3, column=0, sticky="w", padx=12)

        lineas = []
        if e["tengo"]:
            lineas.append("Tienes: " + ", ".join(nom(i) for i in e["tengo"]))
        if e["sustituidos"]:
            lineas.append("Sustituyes: " + ", ".join(f"{nom(a)} → {nom(b)}" for a, b in e["sustituidos"]))
        if e["faltan"]:
            partes = []
            for i, esencial, sugs in e["faltan"]:
                t = nom(i) + ("" if esencial else " (opcional)")
                if sugs:
                    t += " [o " + "/".join(nom(s) for s in sugs) + "]"
                partes.append(t)
            lineas.append("Te falta: " + ", ".join(partes))
        if e["omitidos"]:
            lineas.append("Omitido por tus restricciones: " + ", ".join(nom(i) for i in e["omitidos"]))
        ctk.CTkLabel(card, text="\n".join(lineas), justify="left", wraplength=620, anchor="w").grid(
            row=4, column=0, sticky="w", padx=12, pady=4)
        ctk.CTkButton(card, text="Ver receta", width=110,
                      command=lambda ev=e: VentanaReceta(self, ev)).grid(row=0, column=1, rowspan=2, padx=12, pady=8)

    # ---------------- acciones ----------------
    def cocinar(self, usados):
        """El usuario cocino: se gastan ingredientes y el sistema se readapta."""
        for i in usados:
            if i in self.vars_ing:
                self.vars_ing[i].set(False)
        self.refrescar()

    def abrir_admin(self):
        VentanaAdmin(self)

    def recargar_catalogo(self):
        self.catalogo = db.cargar_catalogo(self.con)
        self.refrescar()
