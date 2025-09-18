import sqlite3

def crear_tabla_consejos():
    conn = sqlite3.connect('ecoguard.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consejos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autor TEXT NOT NULL,
            contenido TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Ejecuta esta función una vez al iniciar
crear_tabla_consejos()