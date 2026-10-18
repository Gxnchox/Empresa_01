import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'dif_tecamac.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')

def inicializar_db_programas_nutricionales():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS programas_nutricionales (
            folio TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            curp TEXT NOT NULL,
            estudio_socioeconomico TEXT,
            curp_doc TEXT,
            comprobante_domicilio TEXT,
            ine_doc TEXT,
            dictamen_medico TEXT
        )
    ''')
    conn.commit()
    conn.close()

def generar_siguiente_folio():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT folio FROM programas_nutricionales ORDER BY folio DESC LIMIT 1')
    ultimo = cursor.fetchone()
    conn.close()
    if ultimo and ultimo[0]:
        try:
            num = int(ultimo[0].split('-')[-1]) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    return f"PN-2026-{num:04d}"

def registrar_beneficiario_nutricional(nombre, curp, archivos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    folio = generar_siguiente_folio()

    cursor.execute('''
        INSERT INTO programas_nutricionales (folio, nombre, curp, estudio_socioeconomico, curp_doc, comprobante_domicilio, ine_doc, dictamen_medico)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        folio, nombre, curp,
        archivos.get('estudio_socioeconomico'),
        archivos.get('curp_doc'),
        archivos.get('comprobante_domicilio'),
        archivos.get('ine_doc'),
        archivos.get('dictamen_medico')
    ))
    conn.commit()
    conn.close()

def obtener_beneficiarios_nutricionales(busqueda=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if busqueda:
        query = "%" + busqueda + "%"
        cursor.execute('SELECT * FROM programas_nutricionales WHERE nombre LIKE ? OR curp LIKE ? OR folio LIKE ?', (query, query, query))
    else:
        cursor.execute('SELECT * FROM programas_nutricionales')
    beneficiarios = cursor.fetchall()
    conn.close()
    return beneficiarios

def eliminar_beneficiario_nutricional(folio):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM programas_nutricionales WHERE folio = ?', (folio,))
    conn.commit()
    conn.close()