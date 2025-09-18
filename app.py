from flask import Flask, render_template, request, redirect
import sqlite3
from googletrans import Translator
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

# ✅ Carpeta para imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔹 Traducir texto
def traducir_a_ingles(texto):
    translator = Translator()
    traduccion = translator.translate(texto, src='es', dest='en')
    return traduccion.text

# 🔹 Crear tabla de consejos con traducción
def crear_tabla_consejos():
    conn = sqlite3.connect('ecoguard.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consejos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autor TEXT NOT NULL,
            contenido TEXT NOT NULL,
            contenido_en TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# 🔹 Crear tabla de reportes con traducción
def crear_tabla_reportes():
    conn = sqlite3.connect('ecoguard.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ubicacion TEXT,
            descripcion TEXT,
            descripcion_en TEXT,
            imagen TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# 🔹 Agregar columna contenido_en si no existe
def agregar_columna_contenido_en():
    conn = sqlite3.connect('ecoguard.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE consejos ADD COLUMN contenido_en TEXT")
        print("✅ Columna 'contenido_en' agregada correctamente.")
    except sqlite3.OperationalError as e:
        print("⚠️ Ya existe la columna o hubo un error:", e)
    conn.commit()
    conn.close()

# 🔹 Agregar columna descripcion_en si no existe
def agregar_columna_descripcion_en():
    conn = sqlite3.connect('ecoguard.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE reportes ADD COLUMN descripcion_en TEXT")
        print("✅ Columna 'descripcion_en' agregada correctamente.")
    except sqlite3.OperationalError as e:
        print("⚠️ Ya existe la columna o hubo un error:", e)
    conn.commit()
    conn.close()

# 🔹 Traducir consejos antiguos sin contenido_en
def traducir_consejos_antiguos():
    conn = sqlite3.connect('ecoguard.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, contenido FROM consejos WHERE contenido_en IS NULL OR contenido_en = ''")
    consejos_sin_traducir = cursor.fetchall()

    for id_consejo, contenido in consejos_sin_traducir:
        contenido_en = traducir_a_ingles(contenido)
        cursor.execute("UPDATE consejos SET contenido_en = ? WHERE id = ?", (contenido_en, id_consejo))
        print(f"✅ Consejo {id_consejo} traducido.")

    conn.commit()
    conn.close()

# 🔹 Traducir reportes antiguos sin descripcion_en
def traducir_reportes_antiguos():
    conn = sqlite3.connect('ecoguard.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, descripcion FROM reportes WHERE descripcion_en IS NULL OR descripcion_en = ''")
    reportes_sin_traducir = cursor.fetchall()

    for id_reporte, descripcion in reportes_sin_traducir:
        descripcion_en = traducir_a_ingles(descripcion)
        cursor.execute("UPDATE reportes SET descripcion_en = ? WHERE id = ?", (descripcion_en, id_reporte))
        print(f"✅ Reporte {id_reporte} traducido.")

    conn.commit()
    conn.close()

# 🔹 Guardar consejo con traducción
def guardar_consejo(autor, contenido):
    contenido_en = traducir_a_ingles(contenido)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('ecoguard.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO consejos (autor, contenido, contenido_en, fecha)
        VALUES (?, ?, ?, ?)
    """, (autor, contenido, contenido_en, fecha))
    conn.commit()
    conn.close()

# 🔹 Obtener consejos
def obtener_consejos():
    conn = sqlite3.connect('ecoguard.db')
    cursor = conn.cursor()
    cursor.execute("SELECT autor, contenido, contenido_en, fecha FROM consejos ORDER BY fecha DESC")
    consejos = cursor.fetchall()
    conn.close()
    return consejos

# 🔹 Página principal
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        location = request.form["location"]
        photo = request.files["photo"]
        return render_template("index.html", message="¡Reporte enviado con éxito!")
    return render_template("index.html")

# 🔹 Nuevo consejo
@app.route("/nuevo_consejo", methods=["GET", "POST"])
def nuevo_consejo():
    if request.method == "POST":
        autor = request.form["autor"]
        contenido = request.form["contenido"]
        guardar_consejo(autor, contenido)
        return redirect("/consejos")
    return render_template("formulario.html")

# 🔹 Ver consejos con traducción ya guardada
@app.route("/consejos")
def ver_consejos():
    consejos = obtener_consejos()
    return render_template("consejos.html", consejos=consejos)

# 🔹 Ver reportes con traducción ya guardada
@app.route("/reportes")
def ver_reportes():
    conn = sqlite3.connect('ecoguard.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ubicacion, descripcion, descripcion_en, imagen, fecha FROM reportes ORDER BY fecha DESC")
    datos = cursor.fetchall()
    conn.close()

    reportes = []
    for ubicacion, descripcion, descripcion_en, imagen, fecha in datos:
        reportes.append((ubicacion, descripcion, descripcion_en, imagen, fecha))

    return render_template("reportes.html", reportes=reportes)

# 🔹 Guardar reporte con traducción
@app.route("/guardar_reporte", methods=["GET", "POST"])
def guardar_reporte():
    if request.method == "POST":
        ubicacion = request.form["ubicacion"]
        descripcion = request.form["descripcion"]
        imagen = request.files["imagen"]

        if imagen:
            nombre_imagen = secure_filename(imagen.filename)
            ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)
            imagen.save(ruta_imagen)

            descripcion_en = traducir_a_ingles(descripcion)

            conn = sqlite3.connect('ecoguard.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reportes (ubicacion, descripcion, descripcion_en, imagen)
                VALUES (?, ?, ?, ?)
            """, (ubicacion, descripcion, descripcion_en, ruta_imagen))
            conn.commit()
            conn.close()

            return render_template("index.html", mensaje="✅ Reporte guardado exitosamente")

        return render_template("index.html", mensaje="⚠️ Error al subir la imagen")

    return redirect("/")

# 🔹 Ejecutar la app

if __name__ == "__main__":
    crear_tabla_consejos()
    crear_tabla_reportes()
    agregar_columna_contenido_en()
    traducir_consejos_antiguos()
    agregar_columna_descripcion_en()
    traducir_reportes_antiguos()
    app.run(host='0.0.0.0', port=5000)