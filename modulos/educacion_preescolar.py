import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'dif_tecamac.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')

def inicializar_db_educacion_preescolar():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS educacion_preescolar (
            folio TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            curp TEXT NOT NULL,
            acta_nacimiento TEXT,
            curp_doc TEXT,
            comprobante_domicilio TEXT,
            certificado_medico TEXT,
            foto TEXT,
            ine_tutor TEXT
        )
    ''')
    conn.commit()
    conn.close()

def generar_siguiente_folio():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT folio FROM educacion_preescolar ORDER BY folio DESC LIMIT 1')
    ultimo = cursor.fetchone()
    conn.close()
    if ultimo and ultimo[0]:
        try:
            num = int(ultimo[0].split('-')[-1]) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    return f"EP-2026-{num:04d}"

def registrar_alumno_preescolar(nombre, curp, archivos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    folio = generar_siguiente_folio()

    cursor.execute('''
        INSERT INTO educacion_preescolar (folio, nombre, curp, acta_nacimiento, curp_doc, comprobante_domicilio, certificado_medico, foto, ine_tutor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        folio, nombre, curp,
        archivos.get('acta_nacimiento'),
        archivos.get('curp_doc'),
        archivos.get('comprobante_domicilio'),
        archivos.get('certificado_medico'),
        archivos.get('foto'),
        archivos.get('ine_tutor')
    ))
    conn.commit()
    conn.close()

def obtener_alumnos_preescolar(busqueda=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if busqueda:
        query = "%" + busqueda + "%"
        cursor.execute('SELECT * FROM educacion_preescolar WHERE nombre LIKE ? OR curp LIKE ? OR folio LIKE ?', (query, query, query))
    else:
        cursor.execute('SELECT * FROM educacion_preescolar')
    alumnos = cursor.fetchall()
    conn.close()
    return alumnos

def eliminar_alumno_preescolar(folio):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM educacion_preescolar WHERE folio = ?', (folio,))
    conn.commit()
    conn.close()