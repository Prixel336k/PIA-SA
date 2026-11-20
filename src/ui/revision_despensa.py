"""Flujo de actualización rápida: muestra la despensa comprada el día anterior para quitar lo que ya se acabó."""
from datetime import date
import customtkinter as ctk

import db
from ui.estilo import (
    BG_CREMA, CARD_BLANCO, TERRACOTA, TERRACOTA_HOVER, VERDE_COCINA,
    GRIS_CHIP, GRIS_TEXTO, etiqueta_ing
)


class VentanaRevisionDespensa(ctk.CTkToplevel):
    """Ventana amigable para que el usuario desmarque rápido lo que ya se terminó de la compra anterior."""

    def __init__(self, app, fecha_guardada):
        super().__init__(app)
        self.app = app
        self.title("🛒 Revisión rápida de tu alacena")
        self.geometry("680x560")
        self.configure(fg_color=BG_CREMA)
        self.after(150, self.focus)

        # Encabezado cálido
        enc = ctk.CTkFrame(self, fg_color=TERRACOTA, corner_radius=12)
        enc.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(
            enc,
            text=f"🧺 Tu mandado del {fecha_guardada}",
            font=("Segoe UI", 20, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkLabel(
            enc,
            text="Toca los ingredientes que YA SE TE ACABARON para quitarlos de tu alacena:",
            font=("Segoe UI", 13),
            text_color="#FFF3E0"
        ).pack(anchor="w", padx=16, pady=(0, 10))

        # Área con los ingredientes que estaban en la despensa
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color=CARD_BLANCO, corner_radius=12,
            label_text="Ingredientes que tenías registrados (en verde = aún tienes, en gris = ya se acabó)"
        )
        self.scroll.pack(fill="both", expand=True, padx=16, pady=8)
        for col in range(3):
            self.scroll.grid_columnconfigure(col, weight=1)

        self.botones = {}
        actuales = [i for i in app.lista_ings if app.vars_ing[i["id"]].get()]

        if not actuales:
            ctk.CTkLabel(
                self.scroll,
                text="Tu alacena estaba vacía. Puedes llenar el mandado básico abajo.",
                font=("Segoe UI", 14), text_color=GRIS_TEXTO
            ).grid(row=0, column=0, columnspan=3, pady=30)
        else:
            for idx, ing in enumerate(actuales):
                iid = ing["id"]
                btn = ctk.CTkButton(
                    self.scroll,
                    text="",
                    height=44,
                    corner_radius=10,
                    font=("Segoe UI", 13, "bold"),
                    command=lambda i=iid: self._alternar(i)
                )
                btn.grid(row=idx // 3, column=idx % 3, sticky="ew", padx=6, pady=6)
                self.botones[iid] = (btn, ing["nombre"])
                self._pintar_boton(iid)

        # Barra inferior de confirmación
        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.pack(fill="x", padx=16, pady=(4, 14))
        ctk.CTkButton(
            pie,
            text="➕Hice mandado hoy (cargar básicos de casa)",
            fg_color="#6D4C41", hover_color="#4E342E",
            height=42, font=("Segoe UI", 13, "bold"),
            command=self._cargar_mandado
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            pie,
            text="✔ Guardar mi alacena actualizada y ver qué cocinar hoy",
            fg_color=VERDE_COCINA, hover_color="#1B5E20",
            height=42, font=("Segoe UI", 14, "bold"),
            command=self._confirmar
        ).pack(side="right", fill="x", expand=True)

    def _pintar_boton(self, iid):
        btn, nombre = self.botones[iid]
        activo = self.app.vars_ing[iid].get()
        if activo:
            btn.configure(
                text=f"✔ {etiqueta_ing(nombre)}",
                fg_color=VERDE_COCINA, hover_color="#1B5E20", text_color="white"
            )
        else:
            btn.configure(
                text=f"✖ {etiqueta_ing(nombre)} (se acabó)",
                fg_color=GRIS_CHIP, hover_color="#E0D8CC", text_color="#8D6E63"
            )

    def _alternar(self, iid):
        actual = self.app.vars_ing[iid].get()
        self.app.vars_ing[iid].set(not actual)
        self._pintar_boton(iid)

    def _cargar_mandado(self):
        self.app.cargar_mandado_basico()
        self.destroy()

    def _confirmar(self):
        db.set_config(self.app.con, "fecha_despensa", date.today().isoformat())
        self.app.ocultar_alerta_dia()
        self.app._pintar_ingredientes()
        self.app.refrescar()
        self.destroy()
