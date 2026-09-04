import os
import sqlite3
from flask import render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DB_PATH = os.path.join(BASE_DIR, 'dif_tecamac.db')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def inicializar_base_datos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicio_social (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            curp TEXT NOT NULL,
            carta TEXT,
            doc_curp TEXT,
            domicilio TEXT,
            foto TEXT,
            aceptacion TEXT,
            bitacora TEXT,
            termino TEXT
        )
    ''')
    conn.commit()
    conn.close()

def registrar_servicio_social():
    inicializar_base_datos()
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if request.method == 'POST':
        # 1. Reemplazar o subir archivo individual directamente en la tabla
        if 'actualizar_campo' in request.form:
            prestador_id = request.form.get('prestador_id')
            campo = request.form.get('actualizar_campo')
            campos_validos = ['carta', 'doc_curp', 'domicilio', 'foto', 'aceptacion', 'bitacora', 'termino']
            
            if campo in campos_validos:
                file_obj = request.files.get(f'file_{campo}')
                if file_obj and file_obj.filename != '' and allowed_file(file_obj.filename):
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT nombre, " + campo + " FROM servicio_social WHERE id = ?", (prestador_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        nombre_alumno = row[0]
                        archivo_anterior = row[1]
                        
                        if archivo_anterior:
                            ruta_ant = os.path.join(UPLOAD_FOLDER, archivo_anterior)
                            if os.path.exists(ruta_ant):
                                os.remove(ruta_ant)
                        
                        filename = secure_filename(f"{nombre_alumno}_{campo}_{file_obj.filename}")
                        file_obj.save(os.path.join(UPLOAD_FOLDER, filename))
                        
                        cursor.execute(f"UPDATE servicio_social SET {campo} = ? WHERE id = ?", (filename, prestador_id))
                        conn.commit()
                    conn.close()
            return redirect(url_for('detalle_servicio_social'))

        # 2. Borrar registro completo del alumno
        if 'eliminar_id' in request.form:
            id_a_borrar = request.form.get('eliminar_id')
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT carta, doc_curp, domicilio, foto, aceptacion, bitacora, termino FROM servicio_social WHERE id = ?', (id_a_borrar,))
            row = cursor.fetchone()
            if row:
                for archivo_nombre in row:
                    if archivo_nombre:
                        ruta_archivo = os.path.join(UPLOAD_FOLDER, archivo_nombre)
                        if os.path.exists(ruta_archivo):
                            os.remove(ruta_archivo)
            cursor.execute('DELETE FROM servicio_social WHERE id = ?', (id_a_borrar,))
            conn.commit()
            conn.close()
            return redirect(url_for('detalle_servicio_social'))

        # 3. Registrar nuevo alumno completo
        nombre = request.form.get('nombre')
        curp_texto = request.form.get('curp')
        
        archivos_keys = ['carta', 'doc_curp', 'domicilio', 'foto', 'aceptacion', 'bitacora', 'termino']
        nombres_archivos = {}
        
        for key in archivos_keys:
            file_obj = request.files.get(f'file_{key}')
            if file_obj and file_obj.filename != '' and allowed_file(file_obj.filename):
                filename = secure_filename(f"{nombre}_{key}_{file_obj.filename}")
                file_obj.save(os.path.join(UPLOAD_FOLDER, filename))
                nombres_archivos[key] = filename
            else:
                nombres_archivos[key] = None

        if nombre and curp_texto:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO servicio_social (nombre, curp, carta, doc_curp, domicilio, foto, aceptacion, bitacora, termino)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre, curp_texto, 
                nombres_archivos['carta'], nombres_archivos['doc_curp'], 
                nombres_archivos['domicilio'], nombres_archivos['foto'], 
                nombres_archivos['aceptacion'], nombres_archivos['bitacora'], 
                nombres_archivos['termino']
            ))
            conn.commit()
            conn.close()
            
        return redirect(url_for('detalle_servicio_social'))
    
    busqueda = request.args.get('q', '').strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if busqueda:
        cursor.execute("SELECT * FROM servicio_social WHERE nombre LIKE ? OR curp LIKE ?", (f'%{busqueda}%', f'%{busqueda}%'))
    else:
        cursor.execute("SELECT * FROM servicio_social")
        
    filas = cursor.fetchall()
    conn.close()
    
    prestadores = []
    for f in filas:
        prestadores.append({
            'id': f[0],
            'nombre': f[1],
            'curp': f[2],
            'archivos': {
                'carta': f[3],
                'doc_curp': f[4],
                'domicilio': f[5],
                'foto': f[6],
                'aceptacion': f[7],
                'bitacora': f[8],
                'termino': f[9]
            }
        })
        
    return render_template('servicio_social.html', area_nombre="Departamento de servicio social", prestadores=prestadores, busqueda=busqueda)

def eliminar_documento_individual(prestador_id, campo):
    campos_validos = ['carta', 'doc_curp', 'domicilio', 'foto', 'aceptacion', 'bitacora', 'termino']
    if campo not in campos_validos:
        return redirect(url_for('detalle_servicio_social'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT {campo} FROM servicio_social WHERE id = ?", (prestador_id,))
    row = cursor.fetchone()
    if row and row[0]:
        ruta_archivo = os.path.join(UPLOAD_FOLDER, row[0])
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
            
    cursor.execute(f"UPDATE servicio_social SET {campo} = NULL WHERE id = ?", (prestador_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('detalle_servicio_social'))