"""Administrador del catalogo: agregar y borrar recetas."""
import customtkinter as ctk
from tkinter import messagebox

import db


class VentanaAdmin(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Administrador del catálogo de recetas")
        self.geometry("900x620")
        self.after(150, self.focus)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.lista = ctk.CTkScrollableFrame(self, width=340, label_text="Recetas registradas")
        self.lista.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        f = ctk.CTkFrame(self)
        f.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        f.grid_columnconfigure(1, weight=1)
        f.grid_rowconfigure(6, weight=1)
        ctk.CTkLabel(f, text="Nueva receta", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=10, pady=10)
        self.e_nombre = self._campo(f, 1, "Nombre")
        self.e_cocina = self._campo(f, 2, "Cocina (ej. Mexicana)")
        self.e_tiempo = self._campo(f, 3, "Tiempo (min)")
        self.m_dif = ctk.CTkOptionMenu(f, values=["Facil", "Media", "Dificil"])
        ctk.CTkLabel(f, text="Dificultad").grid(row=4, column=0, sticky="w", padx=10, pady=4)
        self.m_dif.grid(row=4, column=1, sticky="w", padx=10)
        self.e_esen = self._campo(f, 5, "Ingredientes esenciales\n(separados por coma)")
        self.e_opc = self._campo(f, 6, "Ingredientes opcionales\n(separados por coma)")
        ctk.CTkLabel(f, text="Pasos (uno por línea)").grid(row=7, column=0, sticky="nw", padx=10, pady=4)
        self.t_pasos = ctk.CTkTextbox(f, height=150)
        self.t_pasos.grid(row=7, column=1, sticky="nsew", padx=10, pady=4)
        ctk.CTkButton(f, text="Guardar receta", command=self.guardar).grid(
            row=8, column=0, columnspan=2, pady=10)
        self._pintar()

    def _campo(self, f, fila, texto):
        ctk.CTkLabel(f, text=texto, justify="left").grid(row=fila, column=0, sticky="w", padx=10, pady=4)
        e = ctk.CTkEntry(f)
        e.grid(row=fila, column=1, sticky="ew", padx=10, pady=4)
        return e

    def _pintar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        for r in sorted(self.app.catalogo[1].values(), key=lambda x: (x["cocina"], x["nombre"])):
            fila = ctk.CTkFrame(self.lista, fg_color="transparent")
            fila.pack(fill="x", pady=1)
            ctk.CTkLabel(fila, text=f"[{r['cocina'][:3]}] {r['nombre']}", anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(fila, text="Borrar", width=56, fg_color="#c62828", hover_color="#8e0000",
                          command=lambda rid=r["id"], n=r["nombre"]: self.borrar(rid, n)).pack(side="right")

    def borrar(self, rid, nombre):
        if messagebox.askyesno("Borrar", f"¿Borrar '{nombre}'?", parent=self):
            db.borrar_receta(self.app.con, rid)
            self.app.recargar_catalogo()
            self._pintar()

    def guardar(self):
        try:
            nombre = self.e_nombre.get().strip()
            cocina = self.e_cocina.get().strip().capitalize()
            tiempo = int(self.e_tiempo.get())
            esen = [x.strip().lower() for x in self.e_esen.get().split(",") if x.strip()]
            opc = [x.strip().lower() for x in self.e_opc.get().split(",") if x.strip()]
            pasos = "|".join(p.strip() for p in self.t_pasos.get("1.0", "end").splitlines() if p.strip())
            if not (nombre and cocina and esen and pasos):
                raise ValueError("Completa nombre, cocina, ingredientes esenciales y pasos.")
            db.agregar_receta(self.app.con, nombre, cocina, tiempo, self.m_dif.get(), esen, opc, pasos)
        except Exception as ex:
            messagebox.showerror("No se pudo guardar", str(ex), parent=self)
            return
        self.app.recargar_catalogo()
        self._pintar()
        for e in (self.e_nombre, self.e_cocina, self.e_tiempo, self.e_esen, self.e_opc):
            e.delete(0, "end")
        self.t_pasos.delete("1.0", "end")
        messagebox.showinfo("Listo", "Receta guardada.", parent=self)
