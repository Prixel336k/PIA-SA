"""Ventana con la receta paso a paso."""
import customtkinter as ctk

from logica.adaptacion import cocinar


class VentanaReceta(ctk.CTkToplevel):
    def __init__(self, app, evaluacion):
        super().__init__(app)
        self.app = app
        self.e = evaluacion
        r = evaluacion["receta"]
        ings = app.catalogo[0]
        self.title(r["nombre"])
        self.geometry("560x640")
        self.after(150, self.focus)

        ctk.CTkLabel(self, text=r["nombre"], font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=16, pady=(14, 0))
        ctk.CTkLabel(self, text=f"{r['cocina']}  •  {r['tiempo']} min  •  Dificultad: {r['dificultad']}",
                     text_color="#616161").pack(anchor="w", padx=16)

        caja = ctk.CTkTextbox(self, wrap="word", font=("Segoe UI", 13))
        caja.pack(fill="both", expand=True, padx=16, pady=10)
        caja.insert("end", "INGREDIENTES\n")
        sust = dict(evaluacion["sustituidos"])
        faltan = {i for i, _, _ in evaluacion["faltan"]}
        for i in r["esenciales"] + r["opcionales"]:
            if ings[i]["basico"] or i in evaluacion["omitidos"]:
                continue
            marca = "✔" if i in evaluacion["tengo"] else ("≈" if i in sust else "✖")
            extra = f"  (sustituye: {ings[sust[i]]['nombre']})" if i in sust else ""
            opc = "  [opcional]" if i in r["opcionales"] else ""
            caja.insert("end", f" {marca} {ings[i]['nombre']}{opc}{extra}\n")
        caja.insert("end", "\nPREPARACION\n")
        for n, paso in enumerate(r["pasos"].split("|"), 1):
            caja.insert("end", f" {n}. {paso}\n")
        caja.configure(state="disabled")

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(0, 14))
        ctk.CTkButton(fila, text="Ya lo cociné (descontar de mi despensa)",
                      command=self.cocine).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ctk.CTkButton(fila, text="Cerrar", fg_color="#757575", hover_color="#616161",
                      command=self.destroy).pack(side="left", padx=(4, 0))

    def cocine(self):
        self.app.cocinar(cocinar(None, self.e))
        self.destroy()
