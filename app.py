"""
Rapido Express - Portal de Noticias
Practica 2: Generacion Dinamica de Contenido desde Excel/CSV
"""

import os
import json
import hashlib
from datetime import datetime

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

# Rutas absolutas — funcionan igual en local y en Render
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR   = os.path.join(BASE_DIR, "templates")
UPLOAD_FOLDER  = os.path.join(BASE_DIR, "uploads")
DATA_FOLDER    = os.path.join(BASE_DIR, "data")
META_FILE      = os.path.join(BASE_DIR, "data", "publicaciones.json")

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = "rapido_express_2025"

ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "txt"}
app.config["UPLOAD_FOLDER"]      = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

# Crear carpetas si no existen (importante en Render)
for carpeta in [UPLOAD_FOLDER, DATA_FOLDER]:
    try:
        os.makedirs(carpeta, exist_ok=True)
    except Exception as e:
        print(f"[AVISO] No se pudo crear {carpeta}: {e}")


# ══════════════════════════════════════════════════════════════
# PERSISTENCIA — publicaciones.json
# ══════════════════════════════════════════════════════════════

def cargar_meta():
    """Lee el JSON con el registro de todas las publicaciones."""
    if not os.path.exists(META_FILE):
        return []
    try:
        with open(META_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def guardar_meta(meta):
    """Guarda el registro de publicaciones en el JSON."""
    try:
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[AVISO] guardar_meta: {e}")


def registrar_publicacion(nombre_archivo, df):
    """Registra o actualiza una publicacion en el JSON."""
    meta       = cargar_meta()
    titulo     = extraer_titulo(df)
    imagen_url = extraer_primera_imagen(df)
    resumen    = extraer_resumen(df)
    fecha_pub  = extraer_fecha(df)
    ahora      = datetime.now().strftime("%d/%m/%Y %H:%M")

    for entry in meta:
        if entry["archivo"] == nombre_archivo:
            entry.update({"titulo": titulo, "imagen_url": imagen_url,
                          "resumen": resumen, "fecha_pub": fecha_pub,
                          "fecha_subida": ahora})
            guardar_meta(meta)
            return

    meta.insert(0, {
        "archivo":      nombre_archivo,
        "titulo":       titulo,
        "imagen_url":   imagen_url,
        "resumen":      resumen,
        "fecha_pub":    fecha_pub,
        "fecha_subida": ahora,
        "id":           hashlib.md5(nombre_archivo.encode()).hexdigest()[:8],
    })
    guardar_meta(meta)


# ══════════════════════════════════════════════════════════════
# FUNCIONES DE LECTURA Y EXTRACCION
# ══════════════════════════════════════════════════════════════

def archivo_permitido(nombre):
    return "." in nombre and nombre.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def leer_archivo(ruta):
    ext = ruta.rsplit(".", 1)[1].lower()
    try:
        if ext in ("csv", "txt"):
            df = pd.read_csv(ruta, encoding="utf-8")
        else:
            df = pd.read_excel(ruta)
        df.columns = df.columns.str.strip()
        return df.fillna("")
    except Exception as e:
        print(f"[ERROR leer_archivo] {e}")
        return None


def validar_columnas(df):
    requeridas  = {"tipo", "contenido / url", "estilo"}
    columnas_df = {c.lower() for c in df.columns}
    faltantes   = requeridas - columnas_df
    if faltantes:
        return False, "Faltan columnas obligatorias: " + ", ".join(faltantes)
    return True, ""


def normalizar_col(df, posibles):
    for col in df.columns:
        if col.strip().lower() in [p.lower() for p in posibles]:
            return col
    return None


def extraer_titulo(df):
    col_tipo = normalizar_col(df, ["tipo"])
    col_cont = normalizar_col(df, ["contenido / url", "contenido/url", "contenido", "url"])
    if not col_tipo or not col_cont:
        return "Sin titulo"
    for _, fila in df.iterrows():
        if str(fila[col_tipo]).strip().upper() == "T":
            return str(fila[col_cont]).strip()[:120]
    return "Sin titulo"


def extraer_primera_imagen(df):
    col_tipo = normalizar_col(df, ["tipo"])
    col_cont = normalizar_col(df, ["contenido / url", "contenido/url", "contenido", "url"])
    if not col_tipo or not col_cont:
        return ""
    for _, fila in df.iterrows():
        if str(fila[col_tipo]).strip().upper() == "I":
            url = str(fila[col_cont]).strip()
            if url.startswith("http"):
                return url
    return ""


def extraer_resumen(df):
    col_tipo = normalizar_col(df, ["tipo"])
    col_cont = normalizar_col(df, ["contenido / url", "contenido/url", "contenido", "url"])
    if not col_tipo or not col_cont:
        return ""
    for _, fila in df.iterrows():
        if str(fila[col_tipo]).strip().upper() == "P":
            t = str(fila[col_cont]).strip()
            return t[:160] + ("..." if len(t) > 160 else "")
    return ""


def extraer_fecha(df):
    col_dia  = normalizar_col(df, ["dia", "dia"])
    col_mes  = normalizar_col(df, ["mes"])
    col_anio = normalizar_col(df, ["ano", "anio", "year"])
    partes = []
    if col_dia  and str(df.iloc[0][col_dia]).strip():  partes.append(str(df.iloc[0][col_dia]).strip())
    if col_mes  and str(df.iloc[0][col_mes]).strip():  partes.append(str(df.iloc[0][col_mes]).strip())
    if col_anio and str(df.iloc[0][col_anio]).strip(): partes.append(str(df.iloc[0][col_anio]).strip())
    return " ".join(partes) if partes else datetime.now().strftime("%d/%m/%Y")


def generar_elementos_html(df):
    col_tipo = normalizar_col(df, ["tipo"])
    col_cont = normalizar_col(df, ["contenido / url", "contenido/url", "contenido", "url"])
    col_est  = normalizar_col(df, ["estilo", "style"])
    elementos = []
    for _, fila in df.iterrows():
        tipo      = str(fila[col_tipo]).strip().upper()
        contenido = str(fila[col_cont]).strip() if col_cont else ""
        estilo    = str(fila[col_est]).strip()  if col_est  else ""
        if tipo == "T":
            elementos.append({"tag": "h1",  "contenido": contenido, "estilo": estilo, "tipo": "texto"})
        elif tipo == "ST":
            elementos.append({"tag": "h3",  "contenido": contenido, "estilo": estilo, "tipo": "texto"})
        elif tipo == "P":
            elementos.append({"tag": "p",   "contenido": contenido, "estilo": estilo, "tipo": "texto"})
        elif tipo == "I":
            elementos.append({"tag": "img", "contenido": contenido, "estilo": estilo,
                               "tipo": "imagen", "alt": "Imagen Rapido Express"})
        else:
            print(f"[AVISO] Tipo desconocido ignorado: '{tipo}'")
    return elementos


def obtener_publicaciones_de_archivo(df):
    col_pub  = normalizar_col(df, ["n publicacion", "publicacion", "num publicacion"])
    col_dia  = normalizar_col(df, ["dia"])
    col_mes  = normalizar_col(df, ["mes"])
    col_anio = normalizar_col(df, ["ano", "anio", "year"])
    publicaciones = []
    grupos = df.groupby(df[col_pub], sort=False) if col_pub else [(1, df)]
    for num_pub, grupo in grupos:
        meta = {"num": str(num_pub)}
        if col_dia:  meta["dia"]  = str(grupo.iloc[0][col_dia])
        if col_mes:  meta["mes"]  = str(grupo.iloc[0][col_mes])
        if col_anio: meta["anio"] = str(grupo.iloc[0][col_anio])
        publicaciones.append({"meta": meta, "elementos": generar_elementos_html(grupo)})
    return publicaciones


# ══════════════════════════════════════════════════════════════
# RUTAS FLASK
# ══════════════════════════════════════════════════════════════

@app.route("/")
def portal():
    """Portal principal — muestra todas las noticias como tarjetas."""
    try:
        publicaciones = cargar_meta()
        registrados   = {p["archivo"] for p in publicaciones}

        # Registrar CSV de ejemplo si no esta en el JSON
        ejemplo_ruta = os.path.join(DATA_FOLDER, "ejemplo.csv")
        if os.path.exists(ejemplo_ruta) and "ejemplo.csv" not in registrados:
            df_ej = leer_archivo(ejemplo_ruta)
            if df_ej is not None:
                registrar_publicacion("ejemplo.csv", df_ej)
                publicaciones = cargar_meta()
                registrados   = {p["archivo"] for p in publicaciones}

        # Registrar CSVs en uploads que no esten en el JSON
        if os.path.isdir(UPLOAD_FOLDER):
            for nombre in os.listdir(UPLOAD_FOLDER):
                if nombre.startswith("."):
                    continue
                if nombre not in registrados and archivo_permitido(nombre):
                    try:
                        df_up = leer_archivo(os.path.join(UPLOAD_FOLDER, nombre))
                        if df_up is not None:
                            valido, _ = validar_columnas(df_up)
                            if valido:
                                registrar_publicacion(nombre, df_up)
                    except Exception as e:
                        print(f"[AVISO] {nombre}: {e}")

        publicaciones = cargar_meta()

    except Exception as e:
        print(f"[ERROR portal] {e}")
        publicaciones = []

    error = request.args.get("error", "")
    exito = request.args.get("exito", "")
    return render_template("portal.html",
                           publicaciones=publicaciones,
                           error=error,
                           exito=exito)


@app.route("/subir", methods=["GET", "POST"])
def subir():
    """Formulario de subida de archivo."""
    if request.method == "GET":
        return render_template("subir.html", error="")

    if "archivo" not in request.files:
        return render_template("subir.html", error="No se encontro ningun archivo.")

    archivo = request.files["archivo"]
    if archivo.filename == "":
        return render_template("subir.html", error="No seleccionaste ningun archivo.")
    if not archivo_permitido(archivo.filename):
        return render_template("subir.html", error="Extension no permitida. Usa .csv, .xlsx o .txt")

    nombre_seguro = secure_filename(archivo.filename)
    ruta_guardado = os.path.join(UPLOAD_FOLDER, nombre_seguro)

    try:
        archivo.save(ruta_guardado)
    except Exception as e:
        return render_template("subir.html", error=f"No se pudo guardar el archivo: {e}")

    df = leer_archivo(ruta_guardado)
    if df is None:
        try: os.remove(ruta_guardado)
        except: pass
        return render_template("subir.html", error="No se pudo leer el archivo.")

    valido, msg = validar_columnas(df)
    if not valido:
        try: os.remove(ruta_guardado)
        except: pass
        return render_template("subir.html", error=msg)

    registrar_publicacion(nombre_seguro, df)
    return redirect(url_for("portal") + "?exito=1")


@app.route("/noticia/<nombre_archivo>")
def ver_noticia(nombre_archivo):
    """Muestra el contenido completo de una noticia."""
    nombre_seguro = secure_filename(nombre_archivo)
    ruta = os.path.join(UPLOAD_FOLDER, nombre_seguro)
    if not os.path.exists(ruta):
        ruta = os.path.join(DATA_FOLDER, nombre_seguro)
    if not os.path.exists(ruta):
        return redirect(url_for("portal", error="Archivo no encontrado."))

    df = leer_archivo(ruta)
    if df is None:
        return redirect(url_for("portal", error="No se pudo leer el archivo."))

    valido, msg = validar_columnas(df)
    if not valido:
        return redirect(url_for("portal", error=msg))

    publicaciones = obtener_publicaciones_de_archivo(df)
    todas         = cargar_meta()
    meta_noticia  = next((p for p in todas if p["archivo"] == nombre_seguro), {})

    return render_template("blog.html",
                           publicaciones=publicaciones,
                           nombre_archivo=nombre_seguro,
                           meta_noticia=meta_noticia)


@app.route("/eliminar/<nombre_archivo>", methods=["POST"])
def eliminar_noticia(nombre_archivo):
    """Elimina una noticia del portal."""
    nombre_seguro = secure_filename(nombre_archivo)
    ruta = os.path.join(UPLOAD_FOLDER, nombre_seguro)
    if os.path.exists(ruta):
        try: os.remove(ruta)
        except: pass
    meta = [p for p in cargar_meta() if p["archivo"] != nombre_seguro]
    guardar_meta(meta)
    return redirect(url_for("portal"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", debug=False, port=port)