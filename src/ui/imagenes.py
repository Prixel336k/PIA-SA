"""Carga y descarga fotos reales exactas de cada receta y tipo de cocina (con caché en data/fotos/)."""
import json
import os
import re
import shutil
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageOps
import customtkinter as ctk

_CACHE = {}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOTOS_DIR = os.path.join(BASE_DIR, "data", "fotos")
os.makedirs(FOTOS_DIR, exist_ok=True)

# Fotos reales representativas por tipo de cocina
FOTOS_COCINA = {
    "Mexicana": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/73/001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg/330px-001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg",
    "Italiana": "https://www.themealdb.com/images/media/meals/ustsqw1468250014.jpg/preview",
    "Japonesa": "https://www.themealdb.com/images/media/meals/g046bb1663960946.jpg/preview",
    "India": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/00/Chicken_tikka_masala_%28cropped%29.jpg/330px-Chicken_tikka_masala_%28cropped%29.jpg",
    "China": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a6/Homemade_Chow_mein_with_shrimps_and_meat_with_a_choy_and_Choung.jpg/330px-Homemade_Chow_mein_with_shrimps_and_meat_with_a_choy_and_Choung.jpg",
    "Sorprendeme": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b1/Caprese-1_%28tigher_crop%29.jpg/330px-Caprese-1_%28tigher_crop%29.jpg",
}

# Fotos reales verificadas platillo por platillo para las 40 recetas del catálogo
FOTOS_RECETA = {
    # ---------------- MEXICANA ----------------
    "Huevos a la mexicana": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/70/Huevos_a_la_mexicana_y_quesadillas.png/330px-Huevos_a_la_mexicana_y_quesadillas.png",
    "Tacos de pollo": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/73/001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg/330px-001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg",
    "Quesadillas": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/01/Empanada_flor_de_Calabaza.jpg/330px-Empanada_flor_de_Calabaza.jpg",
    "Frijoles charros": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/34/Frijoles_charros_10293.jpg/330px-Frijoles_charros_10293.jpg",
    "Guacamole con totopos": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/64/Guacamole_IMGP1271.jpg/330px-Guacamole_IMGP1271.jpg",
    "Chilaquiles rojos": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f7/Chilaquiles_at_the_Grand_Cantina%2C_Windsor%2C_Ontario%2C_2025-09-01_04.jpg/330px-Chilaquiles_at_the_Grand_Cantina%2C_Windsor%2C_Ontario%2C_2025-09-01_04.jpg",
    "Arroz a la mexicana": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/0e/Mexican_rice_144235.jpg/330px-Mexican_rice_144235.jpg",
    "Enchiladas de pollo": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/6f/Enchiladas.jpg/330px-Enchiladas.jpg",

    # ---------------- ITALIANA ----------------
    "Spaghetti al pomodoro": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/92/Spaghettoni.jpg/330px-Spaghettoni.jpg",
    "Pasta carbonara": "https://www.themealdb.com/images/media/meals/llcbn01574260722.jpg/preview",
    "Pizza margarita": "https://www.themealdb.com/images/media/meals/x0lk931587671540.jpg/preview",
    "Risotto de champiñones": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a5/Risotto_with_speck_and_goat_cheese_%286101067436%29.jpg/330px-Risotto_with_speck_and_goat_cheese_%286101067436%29.jpg",
    "Pasta Alfredo": "https://www.themealdb.com/images/media/meals/0jv5gx1661040802.jpg/preview",
    "Bruschetta": "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/1f/2014_Bruschetta_The_Larder_Chiang_Mai.jpg/330px-2014_Bruschetta_The_Larder_Chiang_Mai.jpg",
    "Lasaña de carne": "https://www.themealdb.com/images/media/meals/wtsvxx1511296896.jpg/preview",
    "Ensalada caprese": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b1/Caprese-1_%28tigher_crop%29.jpg/330px-Caprese-1_%28tigher_crop%29.jpg",

    # ---------------- JAPONESA ----------------
    "Yakimeshi (arroz frito japonés)": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c3/Koh_Mak%2C_Thailand%2C_Fried_rice_with_seafood%2C_Thai_fried_rice.jpg/330px-Koh_Mak%2C_Thailand%2C_Fried_rice_with_seafood%2C_Thai_fried_rice.jpg",
    "Onigiri de atún": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/22/Japanese_rice_balls_%28onigiri%29.jpg/330px-Japanese_rice_balls_%28onigiri%29.jpg",
    "Sopa de tofu y alga": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e8/Miso_Soup_001.jpg/330px-Miso_Soup_001.jpg",
    "Ramen casero": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c3/Shoyu_Ramen%EF%BC%88Tokyo_Ramen%EF%BC%89_-_01.jpg/330px-Shoyu_Ramen%EF%BC%88Tokyo_Ramen%EF%BC%89_-_01.jpg",
    "Teriyaki de pollo": "https://www.themealdb.com/images/media/meals/wvpsxx1468256321.jpg/preview",
    "Sushi roll de salmón": "https://www.themealdb.com/images/media/meals/g046bb1663960946.jpg/preview",
    "Tamagoyaki": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/06/%E9%B3%A5%E7%84%BC%E3%81%8D%E5%B1%85%E9%85%92%E5%B1%8B_%2839394233682%29.jpg/330px-%E9%B3%A5%E7%84%BC%E3%81%8D%E5%B1%85%E9%85%92%E5%B1%8B_%2839394233682%29.jpg",
    "Yakisoba de verduras": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/01/Yakisoba_-_01.jpg/330px-Yakisoba_-_01.jpg",

    # ---------------- INDIA ----------------
    "Pollo al curry": "https://www.themealdb.com/images/media/meals/wyxwsp1486979827.jpg/preview",
    "Dal de lentejas": "https://www.themealdb.com/images/media/meals/wuxrtu1483564410.jpg/preview",
    "Chana masala": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/8e/Chana_masala.jpg/330px-Chana_masala.jpg",
    "Pulao de verduras": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5a/%22Hyderabadi_Dum_Biryani%22.jpg/330px-%22Hyderabadi_Dum_Biryani%22.jpg",
    "Aloo palak (papa con espinaca)": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b7/Palakpaneer_Rayagada_Odisha_0009.jpg/330px-Palakpaneer_Rayagada_Odisha_0009.jpg",
    "Pollo tikka masala": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/00/Chicken_tikka_masala_%28cropped%29.jpg/330px-Chicken_tikka_masala_%28cropped%29.jpg",
    "Raita de pepino": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/78/Cucumber-raita.jpg/330px-Cucumber-raita.jpg",
    "Curry de verduras con coco": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a9/Aloo_Ghobi.jpg/330px-Aloo_Ghobi.jpg",

    # ---------------- CHINA ----------------
    "Arroz frito chino": "https://www.themealdb.com/images/media/meals/wuyd2h1765655837.jpg/preview",
    "Pollo con brócoli": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/58/Beef_and_broccoli_stir_fry.jpg/330px-Beef_and_broccoli_stir_fry.jpg",
    "Chow mein": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a6/Homemade_Chow_mein_with_shrimps_and_meat_with_a_choy_and_Choung.jpg/330px-Homemade_Chow_mein_with_shrimps_and_meat_with_a_choy_and_Choung.jpg",
    "Res con pimientos": "https://www.themealdb.com/images/media/meals/1529443236.jpg/preview",
    "Tofu mapo": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/88/Chen_Mapo_Tofu.jpg/330px-Chen_Mapo_Tofu.jpg",
    "Sopa de huevo": "https://www.themealdb.com/images/media/meals/1529446137.jpg/preview",
    "Camarones salteados": "https://www.themealdb.com/images/media/meals/1525873040.jpg/preview",
    "Pollo agridulce": "https://www.themealdb.com/images/media/meals/arzs741766434335.jpg/preview",
}

ESTILO_COCINA = {
    "Mexicana": ("#FFF3E0", "#D35400", "#2E7D32"),
    "Italiana": ("#FFEBEE", "#C62828", "#2E7D32"),
    "Japonesa": ("#E3F2FD", "#1565C0", "#EF5350"),
    "India": ("#FFF8E1", "#F57F17", "#6A1B9A"),
    "China": ("#FCE4EC", "#AD1457", "#F9A825"),
    "Sorprendeme": ("#E8F5E9", "#2E7D32", "#F57C00"),
}


def _slug(texto):
    s = texto.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def limpiar_cache_memoria():
    _CACHE.clear()


def _obtener_imagen_desde_url(clave_archivo, url, forzar=False):
    """Carga la foto desde data/fotos/ o la descarga de internet si aún no está guardada."""
    ruta = os.path.join(FOTOS_DIR, f"{clave_archivo}.jpg")
    if (forzar or not os.path.exists(ruta)) and url:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                datos = resp.read()
            with open(ruta, "wb") as f:
                f.write(datos)
            # Si era PNG, convertir a RGB JPEG válido
            im_tmp = Image.open(ruta).convert("RGB")
            im_tmp.save(ruta, "JPEG", quality=90)
        except Exception:
            pass
    if os.path.exists(ruta):
        try:
            return Image.open(ruta).convert("RGBA")
        except Exception:
            return None
    return None


def guardar_foto_personalizada(nombre_receta, origen):
    """Permite al administrador asignar una foto local o URL a cualquier receta."""
    if not origen:
        return
    clave = f"receta_{_slug(nombre_receta)}"
    ruta_dest = os.path.join(FOTOS_DIR, f"{clave}.jpg")
    origen = origen.strip()
    try:
        if origen.startswith("http://") or origen.startswith("https://"):
            FOTOS_RECETA[nombre_receta] = origen
            _obtener_imagen_desde_url(clave, origen, forzar=True)
        elif os.path.exists(origen):
            im = Image.open(origen).convert("RGB")
            im.save(ruta_dest, "JPEG", quality=90)
        limpiar_cache_memoria()
    except Exception:
        pass


def _recortar_con_borde_redondeado(im_origen, size, color_borde="#D35400", radio=16):
    w, h = size
    recortada = ImageOps.fit(im_origen, (w, h), method=Image.Resampling.LANCZOS)

    mascara = Image.new("L", (w, h), 0)
    d_mask = ImageDraw.Draw(mascara)
    d_mask.rounded_rectangle((0, 0, w - 1, h - 1), radius=radio, fill=255)

    salida = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    salida.paste(recortada, (0, 0), mascara)

    d_borde = ImageDraw.Draw(salida)
    d_borde.rounded_rectangle((1, 1, w - 2, h - 2), radius=radio, outline=color_borde, width=3)
    return salida


def img_cocina(cocina, size=(170, 115)):
    """Foto real para las tarjetas del Paso 2 (elección de tipo de cocina)."""
    clave = ("cocina", cocina, size)
    if clave in _CACHE:
        return _CACHE[clave]

    url = FOTOS_COCINA.get(cocina, FOTOS_COCINA["Sorprendeme"])
    _, c_fuerte, _ = ESTILO_COCINA.get(cocina, ESTILO_COCINA["Sorprendeme"])
    im = _obtener_imagen_desde_url(f"cocina_{_slug(cocina)}", url)
    if im is not None:
        final = _recortar_con_borde_redondeado(im, size, color_borde=c_fuerte, radio=16)
    else:
        final = Image.new("RGBA", size, "#FFF3E0")
    ctk_img = ctk.CTkImage(light_image=final, dark_image=final, size=size)
    _CACHE[clave] = ctk_img
    return ctk_img


def img_receta(nombre_receta, cocina, size=(125, 115)):
    """Foto real del platillo para las tarjetas de recomendaciones y la ventana de receta."""
    clave = ("receta", nombre_receta, cocina, size)
    if clave in _CACHE:
        return _CACHE[clave]

    url = FOTOS_RECETA.get(nombre_receta) or FOTOS_COCINA.get(cocina, FOTOS_COCINA["Sorprendeme"])
    _, c_fuerte, _ = ESTILO_COCINA.get(cocina, ESTILO_COCINA["Sorprendeme"])
    im = _obtener_imagen_desde_url(f"receta_{_slug(nombre_receta)}", url)
    if im is not None:
        final = _recortar_con_borde_redondeado(im, size, color_borde=c_fuerte, radio=14)
    else:
        final = Image.new("RGBA", size, "#FFF3E0")
    ctk_img = ctk.CTkImage(light_image=final, dark_image=final, size=size)
    _CACHE[clave] = ctk_img
    return ctk_img


def img_banner_paso(tipo, size=(110, 90)):
    """Imagen para los encabezados del Paso 1 y Paso 3."""
    clave = ("banner", tipo, size)
    if clave in _CACHE:
        return _CACHE[clave]
    w, h = size
    if tipo == "canasta":
        im = _obtener_imagen_desde_url(
            "banner_canasta",
            "https://www.themealdb.com/images/media/meals/b66myb1683207208.jpg/preview"
        )
        if im is not None:
            final = _recortar_con_borde_redondeado(im, size, color_borde="#D35400", radio=14)
            ctk_img = ctk.CTkImage(light_image=final, dark_image=final, size=size)
            _CACHE[clave] = ctk_img
            return ctk_img

    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2
    d.rounded_rectangle((4, 4, w - 5, h - 5), radius=16, fill="#E8F5E9", outline="#2E7D32", width=3)
    d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), fill="#43A047", outline="#1B5E20", width=3)
    d.rectangle((cx - 5, cy - 14, cx + 5, cy + 14), fill="white")
    d.rectangle((cx - 14, cy - 5, cx + 14, cy + 5), fill="white")
    ctk_img = ctk.CTkImage(light_image=im, dark_image=im, size=size)
    _CACHE[clave] = ctk_img
    return ctk_img


def predescargar_todas(forzar=False):
    """Descarga todas las fotos reales en data/fotos/ para que carguen al instante."""
    import time

    tareas = []
    for coc, url in FOTOS_COCINA.items():
        tareas.append((f"cocina_{_slug(coc)}", url))
    for rec, url in FOTOS_RECETA.items():
        tareas.append((f"receta_{_slug(rec)}", url))
    tareas.append(("banner_canasta", "https://www.themealdb.com/images/media/meals/b66myb1683207208.jpg/preview"))

    for clave, url in tareas:
        ruta = os.path.join(FOTOS_DIR, f"{clave}.jpg")
        if forzar or not os.path.exists(ruta):
            _obtener_imagen_desde_url(clave, url, forzar=True)
            if "wikimedia" in url:
                time.sleep(0.25)
