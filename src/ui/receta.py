"""Ventana visual con la fotografía real del platillo y la receta paso a paso."""
import customtkinter as ctk

from logica.adaptacion import cocinar
from ui.imagenes import img_receta
from ui.estilo import (
    BG_CREMA, CARD_BLANCO, TERRACOTA, VERDE_COCINA, ICONOS_COCINA, etiqueta_ing
)


class VentanaReceta(ctk.CTkToplevel):
    def __init__(self, app, evaluacion):
        super().__init__(app)
        self.app = app
        self.e = evaluacion
        r = evaluacion["receta"]
        ings = app.catalogo[0]
        self.title(f"🍲 Receta: {r['nombre']}")
        self.geometry("650x700")
        self.configure(fg_color=BG_CREMA)
        self.after(150, self.focus)

        enc = ctk.CTkFrame(self, fg_color=TERRACOTA, corner_radius=14)
        enc.pack(fill="x", padx=16, pady=(14, 8))
        enc.grid_columnconfigure(1, weight=1)

        foto = img_receta(r["nombre"], r["cocina"], (110, 95))
        ctk.CTkLabel(enc, text="", image=foto).grid(row=0, column=0, rowspan=2, padx=14, pady=10)

        ctk.CTkLabel(
            enc, text=f"🍽️ {r['nombre']}", font=("Segoe UI", 22, "bold"),
            text_color="white", anchor="w"
        ).grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=(14, 2))

        cocina_txt = ICONOS_COCINA.get(r["cocina"], r["cocina"])
        ctk.CTkLabel(
            enc,
            text=f"{cocina_txt}   •   ⏱️ {r['tiempo']} minutos   •   📊 Dificultad: {r['dificultad']}",
            font=("Segoe UI", 13), text_color="#FFF3E0", anchor="w"
        ).grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=(0, 14))

        caja = ctk.CTkTextbox(
            self, wrap="word", font=("Segoe UI", 14),
            fg_color=CARD_BLANCO, corner_radius=12, border_width=1, border_color="#E0D6C8"
        )
        caja.pack(fill="both", expand=True, padx=16, pady=8)
        caja.insert("end", "🧺 INGREDIENTES NECESARIOS\n" + "─" * 42 + "\n")
        sust = dict(evaluacion["sustituidos"])
        for i in r["esenciales"] + r["opcionales"]:
            if ings[i]["basico"] or i in evaluacion["omitidos"]:
                continue
            marca = "✔ (Lo tienes)" if i in evaluacion["tengo"] else (
                "🔄 (Con sustituto)" if i in sust else "🛒 (Te falta)"
            )
            extra = f"  → Usarás: {etiqueta_ing(ings[sust[i]]['nombre'])}" if i in sust else ""
            opc = "  [opcional]" if i in r["opcionales"] else ""
            caja.insert("end", f" • {etiqueta_ing(ings[i]['nombre'])}{opc}   — {marca}{extra}\n")

        caja.insert("end", "\n👩‍🍳 PREPARACIÓN PASO A PASO\n" + "─" * 42 + "\n")
        for n, paso in enumerate(r["pasos"].split("|"), 1):
            caja.insert("end", f"\n Paso {n}: {paso}\n")
        caja.configure(state="disabled")

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(4, 14))
        ctk.CTkButton(
            fila,
            text="🍳 ¡Ya lo cociné! (Descontar ingredientes de mi alacena)",
            fg_color=VERDE_COCINA, hover_color="#1B5E20",
            height=44, font=("Segoe UI", 14, "bold"),
            command=self.cocine
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(
            fila, text="Cerrar", fg_color="#8D6E63", hover_color="#6D4C41",
            height=44, width=100, font=("Segoe UI", 13, "bold"),
            command=self.destroy
        ).pack(side="left")

    def cocine(self):
        self.app.cocinar(cocinar(None, self.e))
        self.destroy()
