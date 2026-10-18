import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'dif_tecamac.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')

def inicializar_db_bibliotecas():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bibliotecas (
            folio TEXT PRIMARY KEY,
            nombre_usuario TEXT NOT NULL,
            curp TEXT NOT NULL,
            solicitud_credencial TEXT,
            curp_doc TEXT,
            comprobante_domicilio TEXT,
            ine_tutor TEXT,
            foto TEXT
        )
    ''')
    conn.commit()
    conn.close()

def generar_siguiente_folio():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT folio FROM bibliotecas ORDER BY folio DESC LIMIT 1')
    ultimo = cursor.fetchone()
    conn.close()
    if ultimo and ultimo[0]:
        try:
            num = int(ultimo[0].split('-')[-1]) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    return f"BIB-2026-{num:04d}"

def registrar_usuario_biblioteca(nombre, curp, archivos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    folio = generar_siguiente_folio()

    cursor.execute('''
        INSERT INTO bibliotecas (folio, nombre_usuario, curp, solicitud_credencial, curp_doc, comprobante_domicilio, ine_tutor, foto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        folio, nombre, curp,
        archivos.get('solicitud_credencial'),
        archivos.get('curp_doc'),
        archivos.get('comprobante_domicilio'),
        archivos.get('ine_tutor'),
        archivos.get('foto')
    ))
    conn.commit()
    conn.close()

def obtener_usuarios_biblioteca(busqueda=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if busqueda:
        query = "%" + busqueda + "%"
        cursor.execute('SELECT * FROM bibliotecas WHERE nombre_usuario LIKE ? OR curp LIKE ? OR folio LIKE ?', (query, query, query))
    else:
        cursor.execute('SELECT * FROM bibliotecas')
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

def eliminar_usuario_biblioteca(folio):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bibliotecas WHERE folio = ?', (folio,))
    conn.commit()
    conn.close()