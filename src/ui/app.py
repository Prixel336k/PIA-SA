"""Interfaz visual con fotografías reales de platillos y cocinas, organizada en pantallas progresivas."""
from datetime import date, timedelta
import customtkinter as ctk

import db
from logica.adaptacion import recomendar, SORPRENDEME
from logica.restricciones import RESTRICCIONES
from ui.receta import VentanaReceta
from ui.admin import VentanaAdmin
from ui.revision_despensa import VentanaRevisionDespensa
from ui.imagenes import img_cocina, img_receta, img_banner_paso
from ui.estilo import (
    BG_CREMA, CARD_BLANCO, TERRACOTA, TERRACOTA_HOVER, VERDE_COCINA,
    VERDE_CLARO, AMARILLO_ALERTA, BORDE_ALERTA, GRIS_CHIP, GRIS_TEXTO,
    ICONOS_COCINA, ICONOS_CATEGORIA, MANDADO_BASICO_CASA, etiqueta_ing
)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

COLORES_NIVEL = {
    0: ("#78909C", "🧺 Tu alacena está vacía — regresa a Mi Alacena para marcar qué tienes"),
    1: ("#2E7D32", "🟢 ¡Listo para cocinar con lo que tienes hoy en casa!"),
    2: ("#F57F17", "🟡 Muy cerca: te falta 1 o 2 ingredientes por comprar"),
    3: ("#E65100", "🟠 Te sugerimos otra cocina que sí puedes preparar hoy"),
    4: ("#C62828", "🔴 Alacena con pocos ingredientes (revisa tu lista de mandado)"),
}

DESCRIPCION_COCINA = {
    "Mexicana": "Tacos, chilaquiles, enchiladas, huevos a la mexicana, arroz y frijoles caseros.",
    "Italiana": "Pastas, espagueti, lasaña, pizza casera, risotto y ensalada fresca.",
    "Japonesa": "Arroz frito yakimeshi, ramen casero, pollo teriyaki, rollos y sopas.",
    "India": "Pollo al curry, lentejas especiadas, arroz con verduras y papas con espinaca.",
    "China": "Arroz frito chino, pollo con brócoli, chow mein, res con pimientos y pollo agridulce.",
    "Sorprendeme": "Revisa todas las cocinas y te sugiere los mejores platillos con tu mandado de hoy.",
}

ICONOS_RESTRICCION = {
    "Vegetariano": ("🥗", "Sin carne, pollo ni pescado"),
    "Sin gluten": ("🌾", "Sin trigo, pasta común ni pan"),
    "Sin lacteos": ("🥛", "Sin leche, queso, crema ni mantequilla"),
    "Sin huevo": ("🥚", "Platillos que no llevan huevo"),
    "Sin mariscos": ("🦐", "Sin camarón ni mariscos"),
    "Sin soya": ("🍶", "Sin salsa de soya ni tofu"),
    "Sin frutos secos": ("🥜", "Libre de nueces y cacahuates"),
}

PASOS_TITULOS = [
    (1, "🧺 1. Tu Mandado"),
    (2, "🌮 2. ¿Qué se antoja?"),
    (3, "🛡️ 3. Cuidados"),
    (4, "🥬 4. Mi Alacena"),
    (5, "🍲 5. ¡Tus Recetas!"),
]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🍲 ¿Qué cocinamos hoy en casa?")
        self.geometry("1180x780")
        self.minsize(980, 660)
        self.configure(fg_color=BG_CREMA)

        self.con = db.inicializar()
        self.catalogo = db.cargar_catalogo(self.con)
        self.lista_ings = db.ingredientes(self.con)
        despensa = db.get_despensa(self.con)
        if not despensa:
            for i in self.lista_ings:
                if i["nombre"] in MANDADO_BASICO_CASA:
                    despensa.add(i["id"])
            ayer = (date.today() - timedelta(days=1)).isoformat()
            db.set_despensa(self.con, despensa, actualizar_fecha=False)
            db.set_config(self.con, "fecha_despensa", ayer)

        self.vars_ing = {i["id"]: ctk.BooleanVar(value=i["id"] in despensa) for i in self.lista_ings}

        guardadas = set(filter(None, db.get_config(self.con, "restricciones").split(";")))
        self.vars_res = {r: ctk.BooleanVar(value=r in guardadas) for r in RESTRICCIONES}
        self.var_antojo = ctk.StringVar(value=db.get_config(self.con, "antojo", SORPRENDEME))
        self.var_categoria = ctk.StringVar(value="Todas")
        self.var_buscar = ctk.StringVar()
        self.var_buscar.trace_add("write", lambda *_: self._pintar_ingredientes())

        self.fecha_alerta = db.get_config(
            self.con, "fecha_despensa", (date.today() - timedelta(days=1)).isoformat()
        )
        self.paso_actual = 1

        self.botones_pasos = {}
        self.botones_antojo = {}
        self.tarjetas_cocina = {}
        self.botones_res = {}
        self.botones_cat = {}
        self.botones_ing = {}
        self.botones_acabados = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._barra_superior()
        self._barra_progreso_pasos()

        self.contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor.grid(row=2, column=0, sticky="nsew", padx=20, pady=(6, 14))
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.contenedor.grid_rowconfigure(0, weight=1)

        self._crear_paso_1_mandado()
        self._crear_paso_2_antojo()
        self._crear_paso_3_cuidados()
        self._crear_paso_4_alacena()
        self._crear_paso_5_recetas()

        self.refrescar(guardar_fecha=False)
        self.ir_a_paso(1)

    # =========================================================================
    # ENCABEZADO Y BARRA DE NAVEGACIÓN
    # =========================================================================
    def _barra_superior(self):
        top = ctk.CTkFrame(self, fg_color=TERRACOTA, corner_radius=0, height=62)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        tit = ctk.CTkFrame(top, fg_color="transparent")
        tit.grid(row=0, column=0, sticky="w", padx=20, pady=8)
        ctk.CTkLabel(
            tit, text="🍲 ¿Qué cocinamos hoy en casa?",
            font=("Segoe UI", 22, "bold"), text_color="white"
        ).pack(anchor="w")
        ctk.CTkLabel(
            tit,
            text="Aprovecha tu mandado, elige tu antojo del día y cocina delicioso sin desperdiciar ingredientes",
            font=("Segoe UI", 12), text_color="#FFE0B2"
        ).pack(anchor="w")

        acc = ctk.CTkFrame(top, fg_color="transparent")
        acc.grid(row=0, column=1, sticky="e", padx=18, pady=8)

        self.lbl_resumen_top = ctk.CTkLabel(
            acc, text="", font=("Segoe UI", 12, "bold"),
            fg_color="#B04100", corner_radius=8, text_color="white", padx=12, pady=6
        )
        self.lbl_resumen_top.pack(side="left", padx=6)

        ctk.CTkButton(
            acc, text="⚙️ Recetario (Admin)",
            fg_color="#5D4037", hover_color="#3E2723",
            height=34, font=("Segoe UI", 12, "bold"),
            command=self.abrir_admin
        ).pack(side="left", padx=4)

    def _barra_progreso_pasos(self):
        barra = ctk.CTkFrame(
            self, fg_color=CARD_BLANCO, corner_radius=12, border_width=1, border_color="#E5DDD3"
        )
        barra.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 4))
        for i in range(len(PASOS_TITULOS)):
            barra.grid_columnconfigure(i, weight=1)

        for col, (num, texto) in enumerate(PASOS_TITULOS):
            btn = ctk.CTkButton(
                barra, text=texto, height=40, corner_radius=10,
                font=("Segoe UI", 13, "bold"),
                command=lambda n=num: self.ir_a_paso(n)
            )
            btn.grid(row=0, column=col, sticky="ew", padx=5, pady=6)
            self.botones_pasos[num] = btn

    def ir_a_paso(self, num):
        self.paso_actual = num
        for n, btn in self.botones_pasos.items():
            if n == num:
                btn.configure(fg_color=TERRACOTA, hover_color=TERRACOTA_HOVER, text_color="white")
            elif n < num:
                btn.configure(fg_color=VERDE_CLARO, hover_color="#C8E6C9", text_color=VERDE_COCINA)
            else:
                btn.configure(fg_color=GRIS_CHIP, hover_color="#E2D9CC", text_color=GRIS_TEXTO)

        for frame in (self.frame_p1, self.frame_p2, self.frame_p3, self.frame_p4, self.frame_p5):
            frame.grid_forget()

        if num == 1:
            self._refrescar_vista_paso_1()
            self.frame_p1.grid(row=0, column=0, sticky="nsew")
        elif num == 2:
            self._actualizar_botones_antojo()
            self.frame_p2.grid(row=0, column=0, sticky="nsew")
        elif num == 3:
            self._actualizar_tarjetas_cuidados()
            self.frame_p3.grid(row=0, column=0, sticky="nsew")
        elif num == 4:
            self._pintar_ingredientes()
            self.frame_p4.grid(row=0, column=0, sticky="nsew")
        elif num == 5:
            self.refrescar(guardar_fecha=False)
            self.frame_p5.grid(row=0, column=0, sticky="nsew")

    # =========================================================================
    # PANTALLA 1: VERIFICACIÓN DE DESPENSA DEL DÍA ANTERIOR
    # =========================================================================
    def _crear_paso_1_mandado(self):
        self.frame_p1 = ctk.CTkFrame(
            self.contenedor, fg_color=CARD_BLANCO, corner_radius=16, border_width=1, border_color="#E5DDD3"
        )
        self.frame_p1.grid_columnconfigure(0, weight=1)
        self.frame_p1.grid_rowconfigure(1, weight=1)

        enc = ctk.CTkFrame(self.frame_p1, fg_color=AMARILLO_ALERTA, corner_radius=14, border_width=2, border_color=BORDE_ALERTA)
        enc.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 12))
        enc.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(enc, text="", image=img_banner_paso("canasta", (110, 90))).grid(
            row=0, column=0, rowspan=2, padx=18, pady=12
        )
        self.lbl_p1_pregunta = ctk.CTkLabel(
            enc,
            text="",
            font=("Segoe UI", 21, "bold"), text_color="#3E2723", anchor="w", justify="left"
        )
        self.lbl_p1_pregunta.grid(row=0, column=1, sticky="ew", padx=(4, 18), pady=(14, 2))
        ctk.CTkLabel(
            enc,
            text="Antes de recomendarte qué cocinar hoy, dinos si tu despensa sigue igual o si ya se terminaron algunos ingredientes:",
            font=("Segoe UI", 14), text_color="#5D4037", anchor="w", justify="left"
        ).grid(row=1, column=1, sticky="ew", padx=(4, 18), pady=(0, 14))

        self.cuerpo_p1 = ctk.CTkFrame(self.frame_p1, fg_color="transparent")
        self.cuerpo_p1.grid(row=1, column=0, sticky="nsew", padx=24, pady=8)
        self.cuerpo_p1.grid_columnconfigure(0, weight=1)
        self.cuerpo_p1.grid_rowconfigure(1, weight=1)

    def _refrescar_vista_paso_1(self):
        for w in self.cuerpo_p1.winfo_children():
            w.destroy()

        fecha = db.get_config(self.con, "fecha_despensa", self.fecha_alerta)
        self.fecha_alerta = fecha
        total_ings = len(self.despensa_actual())
        self.lbl_p1_pregunta.configure(
            text=f"🔔 ¡Hola! ¿Sigues teniendo la misma despensa que el día {fecha}?"
        )

        opciones = ctk.CTkFrame(self.cuerpo_p1, fg_color="transparent")
        opciones.grid(row=0, column=0, sticky="ew", pady=(6, 12))
        for c in range(3):
            opciones.grid_columnconfigure(c, weight=1)

        c_si = ctk.CTkFrame(opciones, fg_color=VERDE_CLARO, corner_radius=14, border_width=2, border_color=VERDE_COCINA)
        c_si.grid(row=0, column=0, sticky="nsew", padx=8, pady=4)
        ctk.CTkLabel(c_si, text="✔ Sí, sigo teniendo lo mismo", font=("Segoe UI", 17, "bold"), text_color=VERDE_COCINA).pack(pady=(16, 4), padx=12)
        ctk.CTkLabel(
            c_si,
            text=f"Conservar mis {total_ings} ingredientes actuales y pasar directo a elegir qué se nos antoja comer hoy.",
            font=("Segoe UI", 13), text_color="#3E2723", wraplength=280
        ).pack(pady=4, padx=14)
        ctk.CTkButton(
            c_si, text="Continuar con mi despensa ➔", fg_color=VERDE_COCINA, hover_color="#1B5E20",
            height=44, font=("Segoe UI", 14, "bold"),
            command=self._accion_si_misma_despensa
        ).pack(fill="x", padx=16, pady=(10, 16))

        c_no = ctk.CTkFrame(opciones, fg_color="#FFF3E0", corner_radius=14, border_width=2, border_color=TERRACOTA)
        c_no.grid(row=0, column=1, sticky="nsew", padx=8, pady=4)
        ctk.CTkLabel(c_no, text="🛒 No, actualiza tu despensa", font=("Segoe UI", 17, "bold"), text_color=TERRACOTA).pack(pady=(16, 4), padx=12)
        ctk.CTkLabel(
            c_no,
            text=f"Ver los ingredientes que tenías el {fecha} para quitar con un toque los que ya se terminaron.",
            font=("Segoe UI", 13), text_color="#3E2723", wraplength=280
        ).pack(pady=4, padx=14)
        ctk.CTkButton(
            c_no, text="Quitar lo que ya se acabó ⬇", fg_color=TERRACOTA, hover_color=TERRACOTA_HOVER,
            height=44, font=("Segoe UI", 14, "bold"),
            command=self._mostrar_lista_acabados_en_p1
        ).pack(fill="x", padx=16, pady=(10, 16))

        c_nuevo = ctk.CTkFrame(opciones, fg_color="#F5F0EB", corner_radius=14, border_width=2, border_color="#8D6E63")
        c_nuevo.grid(row=0, column=2, sticky="nsew", padx=8, pady=4)
        ctk.CTkLabel(c_nuevo, text="🧺 Hice el mandado hoy", font=("Segoe UI", 17, "bold"), text_color="#4E342E").pack(pady=(16, 4), padx=12)
        ctk.CTkLabel(
            c_nuevo,
            text="Cargar el mandado básico de casa o ir a la alacena completa para agregar compras nuevas.",
            font=("Segoe UI", 13), text_color="#3E2723", wraplength=280
        ).pack(pady=4, padx=14)
        ctk.CTkButton(
            c_nuevo, text="Ir a toda mi alacena ➔", fg_color="#6D4C41", hover_color="#4E342E",
            height=44, font=("Segoe UI", 14, "bold"),
            command=lambda: self.ir_a_paso(4)
        ).pack(fill="x", padx=16, pady=(10, 16))

        caja_rev = ctk.CTkFrame(self.cuerpo_p1, fg_color="#FAF6F0", corner_radius=14, border_width=1, border_color="#E0D6C8")
        caja_rev.grid(row=1, column=0, sticky="nsew", pady=(4, 8))
        caja_rev.grid_columnconfigure(0, weight=1)
        caja_rev.grid_rowconfigure(1, weight=1)

        enc_rev = ctk.CTkFrame(caja_rev, fg_color="transparent")
        enc_rev.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 4))
        ctk.CTkLabel(
            enc_rev,
            text=f"🧺 Ingredientes de tu despensa del {fecha} (toca cualquiera que YA SE HAYA ACABADO para quitarlo):",
            font=("Segoe UI", 14, "bold"), text_color="#3E2723"
        ).pack(side="left")

        ctk.CTkButton(
            enc_rev, text="📅 Simular otro día", width=140, height=30,
            fg_color="#8D6E63", hover_color="#5D4037", font=("Segoe UI", 12, "bold"),
            command=self.simular_dia_siguiente
        ).pack(side="right", padx=4)

        scroll_rev = ctk.CTkScrollableFrame(caja_rev, fg_color=CARD_BLANCO, corner_radius=10)
        scroll_rev.grid(row=1, column=0, sticky="nsew", padx=16, pady=6)
        for c in range(4):
            scroll_rev.grid_columnconfigure(c, weight=1)

        self.botones_acabados.clear()
        actuales = [i for i in self.lista_ings if self.vars_ing[i["id"]].get()]
        if not actuales:
            ctk.CTkLabel(
                scroll_rev,
                text="Tu despensa está vacía. Presiona el botón de abajo para cargar el mandado básico de casa.",
                font=("Segoe UI", 14), text_color=GRIS_TEXTO
            ).grid(row=0, column=0, columnspan=4, pady=24)
        else:
            for idx, ing in enumerate(actuales):
                iid = ing["id"]
                b = ctk.CTkButton(
                    scroll_rev, text="", height=44, corner_radius=10,
                    font=("Segoe UI", 13, "bold"),
                    command=lambda i=iid: self._alternar_en_paso_1(i)
                )
                b.grid(row=idx // 4, column=idx % 4, sticky="ew", padx=6, pady=6)
                self.botones_acabados[iid] = (b, ing["nombre"])
                self._pintar_boton_p1(iid)

        pie_rev = ctk.CTkFrame(caja_rev, fg_color="transparent")
        pie_rev.grid(row=2, column=0, sticky="ew", padx=16, pady=(4, 12))
        ctk.CTkButton(
            pie_rev, text="🛒 Cargar mandado básico de casa (12 ingredientes)",
            fg_color="#6D4C41", hover_color="#4E342E", height=40,
            font=("Segoe UI", 13, "bold"), command=self.cargar_mandado_basico
        ).pack(side="left")

        ctk.CTkButton(
            pie_rev, text="✔ Ya actualicé mi despensa — Elegir qué se antoja hoy ➔",
            fg_color=VERDE_COCINA, hover_color="#1B5E20", height=42,
            font=("Segoe UI", 14, "bold"), command=self._accion_si_misma_despensa
        ).pack(side="right")

    def _pintar_boton_p1(self, iid):
        b, nombre = self.botones_acabados[iid]
        if self.vars_ing[iid].get():
            b.configure(
                text=f"✔ {etiqueta_ing(nombre)}",
                fg_color=VERDE_COCINA, hover_color="#1B5E20", text_color="white"
            )
        else:
            b.configure(
                text=f"✖ {etiqueta_ing(nombre)} (se acabó)",
                fg_color=GRIS_CHIP, hover_color="#E0D8CC", text_color="#8D6E63"
            )

    def _alternar_en_paso_1(self, iid):
        self.vars_ing[iid].set(not self.vars_ing[iid].get())
        self._pintar_boton_p1(iid)
        self.refrescar(guardar_fecha=False)

    def _mostrar_lista_acabados_en_p1(self):
        VentanaRevisionDespensa(self, self.fecha_alerta)

    def _accion_si_misma_despensa(self):
        db.set_config(self.con, "fecha_despensa", date.today().isoformat())
        self.fecha_alerta = date.today().isoformat()
        self.refrescar(guardar_fecha=True)
        self.ir_a_paso(2)

    # =========================================================================
    # PANTALLA 2: ¿QUÉ SE ANTOJA HOY? (Tarjetas con fotos reales y clic fluido)
    # =========================================================================
    def _crear_paso_2_antojo(self):
        self.frame_p2 = ctk.CTkFrame(
            self.contenedor, fg_color=CARD_BLANCO, corner_radius=16, border_width=1, border_color="#E5DDD3"
        )
        self.frame_p2.grid_columnconfigure(0, weight=1)
        self.frame_p2.grid_rowconfigure(1, weight=1)

        enc = ctk.CTkFrame(self.frame_p2, fg_color="transparent")
        enc.grid(row=0, column=0, sticky="ew", padx=28, pady=(16, 4))
        enc.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            enc, text="🍽️ ¿Qué tipo de comida se les antoja hoy en casa?",
            font=("Segoe UI", 22, "bold"), text_color="#3E2723"
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            enc,
            text="Haz clic en cualquier tarjeta o foto para elegir tu cocina favorita (puedes cambiarla cuando quieras):",
            font=("Segoe UI", 14), text_color="#6D4C41"
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.lbl_cocina_actual = ctk.CTkLabel(
            enc, text="", font=("Segoe UI", 14, "bold"),
            fg_color=VERDE_CLARO, text_color=VERDE_COCINA, corner_radius=10, padx=14, pady=8
        )
        self.lbl_cocina_actual.grid(row=0, column=1, rowspan=2, sticky="e")

        rejilla = ctk.CTkFrame(self.frame_p2, fg_color="transparent")
        rejilla.grid(row=1, column=0, sticky="nsew", padx=24, pady=6)
        for c in range(3):
            rejilla.grid_columnconfigure(c, weight=1)
        for r in range(2):
            rejilla.grid_rowconfigure(r, weight=1)

        opciones = ["Mexicana", "Italiana", "Japonesa", "India", "China", SORPRENDEME]
        self.tarjetas_cocina = {}
        for idx, op in enumerate(opciones):
            card = ctk.CTkFrame(
                rejilla, fg_color="#FAF6F0", corner_radius=16,
                border_width=3, border_color="#E0D6C8", cursor="hand2"
            )
            card.grid(row=idx // 3, column=idx % 3, sticky="nsew", padx=10, pady=8)
            card.grid_columnconfigure(0, weight=1)

            lbl_img = ctk.CTkLabel(card, text="", image=img_cocina(op, (175, 110)), cursor="hand2")
            lbl_img.pack(pady=(12, 4))

            lbl_tit = ctk.CTkLabel(
                card, text=ICONOS_COCINA.get(op, op),
                font=("Segoe UI", 18, "bold"), text_color="#3E2723", cursor="hand2"
            )
            lbl_tit.pack(pady=(2, 2))

            lbl_desc = ctk.CTkLabel(
                card, text=DESCRIPCION_COCINA.get(op, ""),
                font=("Segoe UI", 12), text_color="#5D4037", wraplength=255,
                justify="center", cursor="hand2"
            )
            lbl_desc.pack(padx=12, pady=(0, 8))

            btn = ctk.CTkButton(
                card, text="Seleccionar", height=38, corner_radius=10,
                font=("Segoe UI", 13, "bold"),
                command=lambda v=op: self.elegir_antojo(v)
            )
            btn.pack(fill="x", padx=16, pady=(2, 12))

            # Vincular el clic a TODA la tarjeta (marco, foto, título y descripción) para que nunca falle al cliquear
            for widget in (card, lbl_img, lbl_tit, lbl_desc):
                widget.bind("<Button-1>", lambda _e, v=op: self.elegir_antojo(v))

            self.botones_antojo[op] = btn
            self.tarjetas_cocina[op] = (card, lbl_tit, lbl_desc, btn)

        nav = ctk.CTkFrame(self.frame_p2, fg_color="transparent")
        nav.grid(row=2, column=0, sticky="ew", padx=28, pady=(4, 16))
        ctk.CTkButton(
            nav, text="⬅ Regresar a Tu Mandado", fg_color="#8D6E63", hover_color="#6D4C41",
            height=44, font=("Segoe UI", 13, "bold"), command=lambda: self.ir_a_paso(1)
        ).pack(side="left")

        ctk.CTkButton(
            nav, text="🍲 ¡Ver directo las Recetas de esta cocina! ➔",
            fg_color=TERRACOTA, hover_color=TERRACOTA_HOVER,
            height=44, font=("Segoe UI", 14, "bold"), command=lambda: self.ir_a_paso(5)
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            nav, text="Siguiente: Cuidados o alergias en casa ➔",
            fg_color=VERDE_COCINA, hover_color="#1B5E20",
            height=44, font=("Segoe UI", 14, "bold"), command=lambda: self.ir_a_paso(3)
        ).pack(side="right")

    def elegir_antojo(self, valor):
        """Selecciona inmediatamente la cocina al tocar cualquier parte de la tarjeta, sin trabarse."""
        self.var_antojo.set(valor)
        self._actualizar_botones_antojo()
        self.refrescar(guardar_fecha=False)

    def _actualizar_botones_antojo(self):
        actual = self.var_antojo.get()
        if hasattr(self, "lbl_cocina_actual"):
            self.lbl_cocina_actual.configure(
                text=f"✔ Cocina elegida: {ICONOS_COCINA.get(actual, actual)}"
            )
        for op, (card, lbl_tit, _lbl_desc, btn) in self.tarjetas_cocina.items():
            if op == actual:
                card.configure(fg_color="#FFE8CC", border_color=TERRACOTA, border_width=4)
                lbl_tit.configure(text_color=TERRACOTA)
                btn.configure(
                    text="✔ COCINA SELECCIONADA",
                    fg_color=VERDE_COCINA, hover_color="#1B5E20", text_color="white"
                )
            else:
                card.configure(fg_color="#FAF6F0", border_color="#E0D6C8", border_width=2)
                lbl_tit.configure(text_color="#3E2723")
                btn.configure(
                    text="Seleccionar esta cocina",
                    fg_color="#6D4C41", hover_color="#4E342E", text_color="white"
                )

    # =========================================================================
    # PANTALLA 3: CUIDADOS O ALERGIAS EN CASA
    # =========================================================================
    def _crear_paso_3_cuidados(self):
        self.frame_p3 = ctk.CTkFrame(
            self.contenedor, fg_color=CARD_BLANCO, corner_radius=16, border_width=1, border_color="#E5DDD3"
        )
        self.frame_p3.grid_columnconfigure(0, weight=1)
        self.frame_p3.grid_rowconfigure(1, weight=1)

        enc = ctk.CTkFrame(self.frame_p3, fg_color="#E8F5E9", corner_radius=14)
        enc.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 10))
        enc.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(enc, text="", image=img_banner_paso("cuidados", (95, 80))).grid(
            row=0, column=0, rowspan=2, padx=16, pady=10
        )
        ctk.CTkLabel(
            enc, text="🛡️ ¿Alguien en la familia evita algún alimento o tiene alergias?",
            font=("Segoe UI", 20, "bold"), text_color="#1B5E20", anchor="w"
        ).grid(row=0, column=1, sticky="ew", pady=(14, 2))
        ctk.CTkLabel(
            enc,
            text="Si nadie tiene restricciones en casa, puedes dejar todo desmarcado y presionar «Siguiente».",
            font=("Segoe UI", 14), text_color="#2E7D32", anchor="w"
        ).grid(row=1, column=1, sticky="ew", pady=(0, 14))

        rejilla = ctk.CTkFrame(self.frame_p3, fg_color="transparent")
        rejilla.grid(row=1, column=0, sticky="nsew", padx=28, pady=10)
        for c in range(3):
            rejilla.grid_columnconfigure(c, weight=1)

        self.tarjetas_res = {}
        for idx, (nombre_res, _var) in enumerate(self.vars_res.items()):
            icono, desc = ICONOS_RESTRICCION.get(nombre_res, ("🛡️", ""))
            card = ctk.CTkFrame(
                rejilla, fg_color="#FAF6F0", corner_radius=14,
                border_width=2, border_color="#E0D6C8", cursor="hand2"
            )
            card.grid(row=idx // 3, column=idx % 3, sticky="nsew", padx=8, pady=8)
            lbl_t = ctk.CTkLabel(
                card, text=f"{icono}  {nombre_res}",
                font=("Segoe UI", 17, "bold"), text_color="#3E2723", cursor="hand2"
            )
            lbl_t.pack(anchor="w", padx=16, pady=(14, 2))
            lbl_d = ctk.CTkLabel(
                card, text=desc, font=("Segoe UI", 12), text_color="#6D4C41", cursor="hand2"
            )
            lbl_d.pack(anchor="w", padx=16, pady=(0, 10))
            btn = ctk.CTkButton(
                card, text="", height=38, corner_radius=10, font=("Segoe UI", 13, "bold"),
                command=lambda r=nombre_res: self._alternar_cuidado(r)
            )
            btn.pack(fill="x", padx=16, pady=(0, 14))
            for w in (card, lbl_t, lbl_d):
                w.bind("<Button-1>", lambda _e, r=nombre_res: self._alternar_cuidado(r))
            self.tarjetas_res[nombre_res] = (card, btn)

        nav = ctk.CTkFrame(self.frame_p3, fg_color="transparent")
        nav.grid(row=2, column=0, sticky="ew", padx=28, pady=(6, 18))
        ctk.CTkButton(
            nav, text="⬅ Regresar a elegir Cocina", fg_color="#8D6E63", hover_color="#6D4C41",
            height=44, font=("Segoe UI", 13, "bold"), command=lambda: self.ir_a_paso(2)
        ).pack(side="left")

        ctk.CTkButton(
            nav, text="🍲 ¡Ir directo a ver mis Recetas recomendadas! ➔",
            fg_color=TERRACOTA, hover_color=TERRACOTA_HOVER,
            height=44, font=("Segoe UI", 14, "bold"), command=lambda: self.ir_a_paso(5)
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            nav, text="🥬 Revisar o agregar cosas a mi Alacena ➔",
            fg_color=VERDE_COCINA, hover_color="#1B5E20",
            height=44, font=("Segoe UI", 13, "bold"), command=lambda: self.ir_a_paso(4)
        ).pack(side="right")

    def _alternar_cuidado(self, nombre_res):
        v = self.vars_res[nombre_res]
        v.set(not v.get())
        self._actualizar_tarjetas_cuidados()
        self.refrescar(guardar_fecha=False)

    def _actualizar_tarjetas_cuidados(self):
        for nombre_res, (card, btn) in self.tarjetas_res.items():
            activo = self.vars_res[nombre_res].get()
            if activo:
                card.configure(fg_color="#FFE8CC", border_color=TERRACOTA, border_width=3)
                btn.configure(
                    text="✔ Activado en casa (toca para quitar)",
                    fg_color=TERRACOTA, hover_color=TERRACOTA_HOVER, text_color="white"
                )
            else:
                card.configure(fg_color="#FAF6F0", border_color="#E0D6C8", border_width=2)
                btn.configure(
                    text="Desactivado (toca para activar)",
                    fg_color=GRIS_CHIP, hover_color="#E0D8CC", text_color="#4E342E"
                )

    # =========================================================================
    # PANTALLA 4: MI ALACENA COMPLETA
    # =========================================================================
    def _crear_paso_4_alacena(self):
        self.frame_p4 = ctk.CTkFrame(
            self.contenedor, fg_color=CARD_BLANCO, corner_radius=16, border_width=1, border_color="#E5DDD3"
        )
        self.frame_p4.grid_columnconfigure(0, weight=1)
        self.frame_p4.grid_rowconfigure(2, weight=1)

        cab = ctk.CTkFrame(self.frame_p4, fg_color="transparent")
        cab.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 4))
        ctk.CTkLabel(
            cab, text="🥬 Tu Alacena y Refrigerador",
            font=("Segoe UI", 21, "bold"), text_color="#3E2723"
        ).pack(side="left")

        self.lbl_cuenta = ctk.CTkLabel(
            cab, text="", font=("Segoe UI", 14, "bold"),
            fg_color=VERDE_CLARO, text_color=VERDE_COCINA, corner_radius=8, padx=12, pady=4
        )
        self.lbl_cuenta.pack(side="right")

        filtros = ctk.CTkFrame(self.frame_p4, fg_color="transparent")
        filtros.grid(row=1, column=0, sticky="ew", padx=24, pady=4)
        filtros.grid_columnconfigure(0, weight=1)

        cats_frame = ctk.CTkFrame(filtros, fg_color="transparent")
        cats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        categorias = ["Todas"] + sorted({i["categoria"] for i in self.lista_ings})
        for c in range(len(categorias)):
            cats_frame.grid_columnconfigure(c, weight=1)

        for idx, cat in enumerate(categorias):
            b = ctk.CTkButton(
                cats_frame, text=ICONOS_CATEGORIA.get(cat, cat),
                height=34, corner_radius=8, font=("Segoe UI", 12, "bold"),
                command=lambda c=cat: self.elegir_categoria(c)
            )
            b.grid(row=0, column=idx, sticky="ew", padx=3)
            self.botones_cat[cat] = b

        barra_busq = ctk.CTkFrame(filtros, fg_color="transparent")
        barra_busq.grid(row=1, column=0, sticky="ew")
        barra_busq.grid_columnconfigure(0, weight=1)

        ctk.CTkEntry(
            barra_busq, textvariable=self.var_buscar, height=38, font=("Segoe UI", 13),
            placeholder_text="🔍 Escribe aquí para buscar un ingrediente rápido (ej. pollo, jitomate, arroz, queso)..."
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            barra_busq, text="🧺 Cargar mandado básico", fg_color=VERDE_COCINA, hover_color="#1B5E20",
            height=38, font=("Segoe UI", 12, "bold"), command=self.cargar_mandado_basico
        ).grid(row=0, column=1, padx=4)

        ctk.CTkButton(
            barra_busq, text="🧹 Vaciar todo", fg_color="#8D6E63", hover_color="#6D4C41",
            height=38, font=("Segoe UI", 12, "bold"), command=self.vaciar
        ).grid(row=0, column=2, padx=(4, 0))

        self.scroll_ing = ctk.CTkScrollableFrame(self.frame_p4, fg_color="#FAF6F0", corner_radius=12)
        self.scroll_ing.grid(row=2, column=0, sticky="nsew", padx=24, pady=6)
        for c in range(4):
            self.scroll_ing.grid_columnconfigure(c, weight=1)

        nav = ctk.CTkFrame(self.frame_p4, fg_color="transparent")
        nav.grid(row=3, column=0, sticky="ew", padx=24, pady=(6, 16))
        ctk.CTkButton(
            nav, text="⬅ Regresar a Cuidados", fg_color="#8D6E63", hover_color="#6D4C41",
            height=44, font=("Segoe UI", 13, "bold"), command=lambda: self.ir_a_paso(3)
        ).pack(side="left")
        ctk.CTkButton(
            nav, text="🍲 ¡Listo! Ver qué platillos puedo cocinar hoy ➔",
            fg_color=TERRACOTA, hover_color=TERRACOTA_HOVER,
            height=46, font=("Segoe UI", 15, "bold"), command=lambda: self.ir_a_paso(5)
        ).pack(side="right")

        self._actualizar_botones_cat()

    # =========================================================================
    # PANTALLA 5: RECETAS RECOMENDADAS (Con foto real de cada platillo)
    # =========================================================================
    def _crear_paso_5_recetas(self):
        self.frame_p5 = ctk.CTkFrame(
            self.contenedor, fg_color=CARD_BLANCO, corner_radius=16, border_width=1, border_color="#E5DDD3"
        )
        self.frame_p5.grid_columnconfigure(0, weight=1)
        self.frame_p5.grid_rowconfigure(1, weight=1)

        self.banner = ctk.CTkLabel(
            self.frame_p5, text="", wraplength=960, justify="left",
            font=("Segoe UI", 15, "bold"),
            text_color="white", corner_radius=12, anchor="w", padx=18, pady=12
        )
        self.banner.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 8))

        self.scroll_res = ctk.CTkScrollableFrame(
            self.frame_p5, fg_color="#FAF6F0", corner_radius=12,
            label_text="🍽️ Platillos recomendados para tu familia hoy",
            label_font=("Segoe UI", 15, "bold")
        )
        self.scroll_res.grid(row=1, column=0, sticky="nsew", padx=24, pady=4)
        self.scroll_res.grid_columnconfigure(0, weight=1)

        nav = ctk.CTkFrame(self.frame_p5, fg_color="transparent")
        nav.grid(row=2, column=0, sticky="ew", padx=24, pady=(6, 16))
        ctk.CTkButton(
            nav, text="⬅ Cambiar ingredientes en mi Alacena", fg_color="#8D6E63", hover_color="#6D4C41",
            height=42, font=("Segoe UI", 13, "bold"), command=lambda: self.ir_a_paso(4)
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            nav, text="🌮 Cambiar antojo de cocina", fg_color=TERRACOTA, hover_color=TERRACOTA_HOVER,
            height=42, font=("Segoe UI", 13, "bold"), command=lambda: self.ir_a_paso(2)
        ).pack(side="left")
        ctk.CTkButton(
            nav, text="🔔 Volver al inicio (Tu Mandado)", fg_color=VERDE_COCINA, hover_color="#1B5E20",
            height=42, font=("Segoe UI", 13, "bold"), command=lambda: self.ir_a_paso(1)
        ).pack(side="right")

    # =========================================================================
    # MÉTODOS AUXILIARES Y MOTOR ADAPTATIVO
    # =========================================================================
    def ocultar_alerta_dia(self):
        pass

    def simular_dia_siguiente(self):
        if not self.despensa_actual():
            self.cargar_mandado_basico()
        ayer = (date.today() - timedelta(days=1)).isoformat()
        db.set_config(self.con, "fecha_despensa", ayer)
        self.fecha_alerta = ayer
        self.ir_a_paso(1)

    def elegir_categoria(self, cat):
        self.var_categoria.set(cat)
        self._actualizar_botones_cat()
        self._pintar_ingredientes()

    def _actualizar_botones_cat(self):
        actual = self.var_categoria.get()
        for cat, btn in self.botones_cat.items():
            if cat == actual:
                btn.configure(fg_color="#5D4037", hover_color="#3E2723", text_color="white")
            else:
                btn.configure(fg_color=GRIS_CHIP, hover_color="#E2D9CC", text_color=GRIS_TEXTO)

    def _pintar_ingredientes(self):
        for w in self.scroll_ing.winfo_children():
            w.destroy()
        self.botones_ing.clear()

        filtro = self.var_buscar.get().strip().lower()
        cat_sel = self.var_categoria.get()

        visibles = [
            ing for ing in self.lista_ings
            if (cat_sel == "Todas" or ing["categoria"] == cat_sel)
            and (not filtro or filtro in ing["nombre"] or filtro in etiqueta_ing(ing["nombre"]).lower())
        ]

        for idx, ing in enumerate(visibles):
            iid = ing["id"]
            btn = ctk.CTkButton(
                self.scroll_ing,
                text="",
                height=44,
                corner_radius=10,
                anchor="w",
                font=("Segoe UI", 13, "bold"),
                command=lambda i=iid: self._toggle_ingrediente(i)
            )
            btn.grid(row=idx // 4, column=idx % 4, sticky="ew", padx=5, pady=5)
            self.botones_ing[iid] = (btn, ing["nombre"])
            self._estilo_chip(iid)

    def _estilo_chip(self, iid):
        if iid not in self.botones_ing:
            return
        btn, nombre = self.botones_ing[iid]
        if self.vars_ing[iid].get():
            btn.configure(
                text=f"✔ {etiqueta_ing(nombre)}",
                fg_color=VERDE_COCINA, hover_color="#1B5E20", text_color="white"
            )
        else:
            btn.configure(
                text=f"   {etiqueta_ing(nombre)}",
                fg_color=GRIS_CHIP, hover_color="#E4DDD2", text_color="#4E342E"
            )

    def _toggle_ingrediente(self, iid):
        self.vars_ing[iid].set(not self.vars_ing[iid].get())
        self._estilo_chip(iid)
        self.refrescar()

    def despensa_actual(self):
        return {i for i, v in self.vars_ing.items() if v.get()}

    def restricciones_actuales(self):
        return [r for r, v in self.vars_res.items() if v.get()]

    def cargar_mandado_basico(self):
        for i in self.lista_ings:
            self.vars_ing[i["id"]].set(i["nombre"] in MANDADO_BASICO_CASA)
        self._pintar_ingredientes()
        self.refrescar(guardar_fecha=True)
        if self.paso_actual == 1:
            self._refrescar_vista_paso_1()

    def vaciar(self):
        for v in self.vars_ing.values():
            v.set(False)
        self._pintar_ingredientes()
        self.refrescar()
        if self.paso_actual == 1:
            self._refrescar_vista_paso_1()

    def refrescar(self, guardar_fecha=True):
        despensa = self.despensa_actual()
        restricciones = self.restricciones_actuales()
        db.set_despensa(self.con, despensa, actualizar_fecha=guardar_fecha)
        db.set_config(self.con, "antojo", self.var_antojo.get())
        db.set_config(self.con, "restricciones", ";".join(restricciones))
        self.lbl_cuenta.configure(text=f"🧺 {len(despensa)} ingredientes en casa")

        antojo_txt = ICONOS_COCINA.get(self.var_antojo.get(), self.var_antojo.get())
        self.lbl_resumen_top.configure(
            text=f"🧺 {len(despensa)} en alacena   •   {antojo_txt}"
        )

        res = recomendar(self.catalogo, despensa, self.var_antojo.get(), restricciones)
        self.resultado = res
        color_banner, encabezado_nivel = COLORES_NIVEL[res["nivel"]]
        extra = f"   •   🛡️ Recetas ocultadas por alergias/cuidados: {res['descartadas']}" if res["descartadas"] else ""
        self.banner.configure(
            text=f"{encabezado_nivel}\n{res['mensaje']}{extra}",
            fg_color=color_banner
        )

        for w in self.scroll_res.winfo_children():
            w.destroy()
        for n, e in enumerate(res["resultados"]):
            self._tarjeta(n, e)

    def _tarjeta(self, fila, e):
        ings = self.catalogo[0]
        r = e["receta"]
        nom = lambda i: etiqueta_ing(ings[i]["nombre"])

        borde = "#66BB6A" if e["cocinable"] else "#FFB74D"
        fondo = VERDE_CLARO if (e["cocinable"] and fila == 0) else CARD_BLANCO
        card = ctk.CTkFrame(
            self.scroll_res, fg_color=fondo, corner_radius=14,
            border_width=2, border_color=borde
        )
        card.grid(row=fila, column=0, sticky="ew", pady=8, padx=6)
        card.grid_columnconfigure(1, weight=1)

        # Columna 0: Fotografía real del platillo
        foto_platillo = img_receta(r["nombre"], r["cocina"], (135, 115))
        lbl_foto = ctk.CTkLabel(card, text="", image=foto_platillo, cursor="hand2")
        lbl_foto.grid(row=0, column=0, rowspan=5, padx=(14, 14), pady=12)
        lbl_foto.bind("<Button-1>", lambda _ev, ev=e: VentanaReceta(self, ev))

        # Columna 1: Información clara y espaciada
        medalla = "⭐ MEJOR OPCIÓN PARA HOY  •  " if fila == 0 else ""
        ctk.CTkLabel(
            card, text=f"{medalla}{r['nombre']}",
            font=("Segoe UI", 19, "bold"), text_color="#2E1C14"
        ).grid(row=0, column=1, sticky="w", padx=4, pady=(12, 0))

        cocina_icono = ICONOS_COCINA.get(r["cocina"], r["cocina"])
        ctk.CTkLabel(
            card,
            text=f"{cocina_icono}   •   ⏱️ {r['tiempo']} minutos   •   📊 Dificultad: {r['dificultad']}",
            font=("Segoe UI", 13), text_color="#6D4C41"
        ).grid(row=1, column=1, sticky="w", padx=4, pady=(0, 4))

        barra = ctk.CTkProgressBar(
            card, height=13, corner_radius=6,
            progress_color=VERDE_COCINA if e["cocinable"] else "#EF6C00"
        )
        barra.set(e["score"] / 100)
        barra.grid(row=2, column=1, sticky="ew", padx=(4, 16), pady=(4, 2))

        estado_txt = (
            f"✔ ¡Ya tienes todo lo necesario en casa! ({e['score']:.0f}% compatible)"
            if e["cocinable"]
            else f"🛒 Te faltan ingredientes principales ({e['score']:.0f}% compatible)"
        )
        ctk.CTkLabel(
            card, text=estado_txt, font=("Segoe UI", 13, "bold"),
            text_color=VERDE_COCINA if e["cocinable"] else "#E65100"
        ).grid(row=3, column=1, sticky="w", padx=4)

        lineas = []
        if e["tengo"]:
            lineas.append("✔ En tu cocina: " + ", ".join(nom(i) for i in e["tengo"]))
        if e["sustituidos"]:
            lineas.append("🔄 Sustituto en casa: " + ", ".join(f"en vez de {nom(a)} usa {nom(b)}" for a, b in e["sustituidos"]))
        if e["faltan"]:
            partes = []
            for i, esencial, sugs in e["faltan"]:
                t = nom(i) + ("" if esencial else " (opcional)")
                if sugs:
                    t += " [o compra " + " / ".join(nom(s) for s in sugs) + "]"
                partes.append(t)
            lineas.append("🛒 Te falta: " + ", ".join(partes))
        if e["omitidos"]:
            lineas.append("🛡️ Omitido por cuidado familiar: " + ", ".join(nom(i) for i in e["omitidos"]))

        ctk.CTkLabel(
            card, text="\n".join(lineas), justify="left",
            wraplength=650, anchor="w", font=("Segoe UI", 13), text_color="#3E2723"
        ).grid(row=4, column=1, sticky="w", padx=4, pady=(4, 12))

        # Columna 2: Botón grande para abrir la receta
        ctk.CTkButton(
            card, text="👩‍🍳 Ver receta\npaso a paso", width=140, height=54,
            corner_radius=12, fg_color=TERRACOTA, hover_color=TERRACOTA_HOVER,
            font=("Segoe UI", 14, "bold"),
            command=lambda ev=e: VentanaReceta(self, ev)
        ).grid(row=0, column=2, rowspan=5, padx=16, pady=12)

    def cocinar(self, usados):
        for i in usados:
            if i in self.vars_ing:
                self.vars_ing[i].set(False)
        self._pintar_ingredientes()
        self.refrescar()

    def abrir_admin(self):
        VentanaAdmin(self)

    def recargar_catalogo(self):
        self.catalogo = db.cargar_catalogo(self.con)
        self.lista_ings = db.ingredientes(self.con)
        for ing in self.lista_ings:
            if ing["id"] not in self.vars_ing:
                self.vars_ing[ing["id"]] = ctk.BooleanVar(value=False)
        ids_validos = {ing["id"] for ing in self.lista_ings}
        for iid in list(self.vars_ing.keys()):
            if iid not in ids_validos:
                del self.vars_ing[iid]
        self._pintar_ingredientes()
        if self.paso_actual == 1:
            self._refrescar_vista_paso_1()
        self.refrescar(guardar_fecha=False)
