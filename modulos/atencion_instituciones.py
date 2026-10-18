import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'dif_tecamac.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')

def inicializar_db_atencion_instituciones():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atencion_instituciones (
            folio TEXT PRIMARY KEY,
            nombre_escuela TEXT NOT NULL,
            cct TEXT NOT NULL,
            oficio_solicitud TEXT,
            plan_trabajo TEXT,
            lista_asistencia TEXT,
            evidencia_fotografica TEXT,
            acta_cierre TEXT
        )
    ''')
    conn.commit()
    conn.close()

def generar_siguiente_folio():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT folio FROM atencion_instituciones ORDER BY folio DESC LIMIT 1')
    ultimo = cursor.fetchone()
    conn.close()
    if ultimo and ultimo[0]:
        try:
            num = int(ultimo[0].split('-')[-1]) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    return f"AIE-2026-{num:04d}"

def registrar_institucion(escuela, cct, archivos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    folio = generar_siguiente_folio()

    cursor.execute('''
        INSERT INTO atencion_instituciones (folio, nombre_escuela, cct, oficio_solicitud, plan_trabajo, lista_asistencia, evidencia_fotografica, acta_cierre)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        folio, escuela, cct,
        archivos.get('oficio_solicitud'),
        archivos.get('plan_trabajo'),
        archivos.get('lista_asistencia'),
        archivos.get('evidencia_fotografica'),
        archivos.get('acta_cierre')
    ))
    conn.commit()
    conn.close()

def obtener_instituciones(busqueda=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if busqueda:
        query = "%" + busqueda + "%"
        cursor.execute('SELECT * FROM atencion_instituciones WHERE nombre_escuela LIKE ? OR cct LIKE ? OR folio LIKE ?', (query, query, query))
    else:
        cursor.execute('SELECT * FROM atencion_instituciones')
    inst = cursor.fetchall()
    conn.close()
    return inst

def eliminar_institucion(folio):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM atencion_instituciones WHERE folio = ?', (folio,))
    conn.commit()
    conn.close()