"""Paleta cálida de cocina casera, íconos y nombres con acentos para una interfaz visual y amigable."""

# Paleta cálida pensada para cocina casera / amas de casa
BG_CREMA = "#FAF6F0"
CARD_BLANCO = "#FFFFFF"
TERRACOTA = "#D35400"
TERRACOTA_HOVER = "#B04100"
VERDE_COCINA = "#2E7D32"
VERDE_CLARO = "#E8F5E9"
VERDE_BORDE = "#66BB6A"
AMARILLO_ALERTA = "#FFF8E1"
BORDE_ALERTA = "#FFA000"
GRIS_CHIP = "#F1ECE4"
GRIS_TEXTO = "#5D4037"

ICONOS_COCINA = {
    "Sorprendeme": "🎲 Sorpréndeme",
    "Mexicana": "🌮 Mexicana",
    "Italiana": "🍝 Italiana",
    "Japonesa": "🍱 Japonesa",
    "India": "🍛 India",
    "China": "🥡 China",
}

ICONOS_CATEGORIA = {
    "Todas": "🧺 Todas",
    "Verduras y frutas": "🥬 Verduras",
    "Carnes": "🥩 Carnes",
    "Lacteos y huevo": "🧀 Lácteos y huevo",
    "Cereales y masas": " tortillas/Cereales",
    "Legumbres": "🫘 Frijol y legumbres",
    "Salsas y especias": "🌶️ Salsas y especias",
    "Pescados y mariscos": "🐟 Pescados",
}

# Corrige el label de cereales
ICONOS_CATEGORIA["Cereales y masas"] = "🌾 Tortillas y pastas"

ICONOS_INGREDIENTE = {
    "pollo": "🍗 Pollo", "res": "🥩 Res", "cerdo": "🥓 Cerdo",
    "carne molida": "🥩 Carne molida", "tocino": "🥓 Tocino",
    "chorizo": "🌭 Chorizo", "jamon": "🍖 Jamón",
    "salmon": "🐟 Salmón", "atun": "🐟 Atún", "camaron": "🦐 Camarón",
    "leche": "🥛 Leche", "queso": "🧀 Queso", "queso parmesano": "🧀 Queso parmesano",
    "mozzarella": "🧀 Mozzarella", "crema": "🥣 Crema", "mantequilla": "🧈 Mantequilla",
    "yogur": "🥣 Yogur", "huevo": "🥚 Huevo",
    "cebolla": "🧅 Cebolla", "ajo": "🧄 Ajo", "jitomate": "🍅 Jitomate",
    "chile": "🌶️ Chile", "papa": "🥔 Papa", "zanahoria": "🥕 Zanahoria",
    "espinaca": "🥬 Espinaca", "brocoli": "🥦 Brócoli", "pimiento": "🫑 Pimiento",
    "champinones": "🍄 Champiñones", "pepino": "🥒 Pepino", "aguacate": "🥑 Aguacate",
    "cilantro": "🌿 Cilantro", "limon": "🍋 Limón", "jengibre": "🫚 Jengibre",
    "col": "🥬 Col", "chicharos": "🫛 Chícharos", "albahaca": "🌿 Albahaca",
    "cebollin": "🌱 Cebollín",
    "arroz": "🍚 Arroz", "pasta": "🍝 Pasta", "fideos": "🍜 Fideos",
    "tortilla de maiz": "🫓 Tortilla de maíz", "tortilla de harina": "🫓 Tortilla de harina",
    "pan": "🍞 Pan", "harina": "🌾 Harina", "alga nori": "🍙 Alga nori",
    "frijol": "🫘 Frijol", "lenteja": "🫘 Lenteja", "garbanzo": "🫘 Garbanzo",
    "tofu": "🧊 Tofu",
    "salsa de soya": "🍶 Salsa de soya", "salsa de tomate": "🥫 Salsa de tomate",
    "curry en polvo": "🍛 Curry en polvo", "garam masala": "🫙 Garam masala",
    "comino": "🫙 Comino", "oregano": "🌿 Orégano", "vinagre de arroz": "🍶 Vinagre de arroz",
    "leche de coco": "🥥 Leche de coco", "miel": "🍯 Miel", "ajonjoli": "🌾 Ajonjolí",
}

MANDADO_BASICO_CASA = [
    "huevo", "jitomate", "cebolla", "chile", "tortilla de maiz",
    "frijol", "arroz", "ajo", "limon", "queso", "pollo", "crema"
]


def etiqueta_ing(nombre):
    return ICONOS_INGREDIENTE.get(nombre, nombre.capitalize())
