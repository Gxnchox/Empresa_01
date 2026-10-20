import os
import sqlite3
from flask import redirect, render_template, request, session, url_for

# Configuración de ruta absoluta unificada para la base de datos
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'datos', 'registros.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


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
            solicitud TEXT,
            plan TEXT
        )
    ''')
  conn.commit()
  conn.close()


def generar_folio_institucional():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('SELECT COUNT(*) FROM atencion_instituciones')
  total = cursor.fetchone()[0]
  conn.close()
  return f'IE-2026-{(total + 1):04d}'


def registrar_atencion_instituciones():
  inicializar_db_atencion_instituciones()
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  if request.method == 'POST' and 'eliminar_folio' in request.form:
    folio_a_eliminar = request.form.get('eliminar_folio')
    cursor.execute(
        'SELECT solicitud, plan FROM atencion_instituciones WHERE folio = ?',
        (folio_a_eliminar,),
    )
    row = cursor.fetchone()
    if row:
      campos_archivos = ['solicitud', 'plan']
      for campo in campos_archivos:
        archivo = row[campo]
        if archivo:
          path_archivo = os.path.join(UPLOAD_FOLDER, archivo)
          if os.path.exists(path_archivo):
            os.remove(path_archivo)

    cursor.execute(
        'DELETE FROM atencion_instituciones WHERE folio = ?', (folio_a_eliminar,)
    )
    conn.commit()
    conn.close()
    return redirect(
        url_for(
            'detalle_area', area_nombre='Atención a instituciones educativas'
        )
    )

  if request.method == 'POST':
    folio_existente = request.form.get('folio_prestador') or request.form.get(
        'folio'
    )
    actualizar_campo = request.form.get('actualizar_campo')

    if folio_existente and actualizar_campo:
      file_key = f'file_{actualizar_campo}'
      file = request.files.get(file_key)
      if file and file.filename != '':
        filename = f'{folio_existente}_{actualizar_campo}_{file.filename}'
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        cursor.execute(
            f'SELECT {actualizar_campo} FROM atencion_instituciones WHERE'
            ' folio = ?',
            (folio_existente,),
        )
        old_file = cursor.fetchone()[0]
        if old_file:
          old_path = os.path.join(UPLOAD_FOLDER, old_file)
          if os.path.exists(old_path):
            os.remove(old_path)

        cursor.execute(
            f'UPDATE atencion_instituciones SET {actualizar_campo} = ? WHERE'
            ' folio = ?',
            (filename, folio_existente),
        )
        conn.commit()
      conn.close()
      return redirect(
          url_for(
              'detalle_area', area_nombre='Atención a instituciones educativas'
          )
      )

    nombre_escuela = request.form.get('nombre_escuela')
    cct = request.form.get('cct')

    if nombre_escuela and cct:
      nuevo_folio = generar_folio_institucional()
      db_campos = ['solicitud', 'plan']
      archivos_guardados = {}
      for campo in db_campos:
        file = request.files.get(f'file_{campo}') or request.files.get(campo)
        if file and file.filename != '':
          filename = f'{nuevo_folio}_{campo}_{file.filename}'
          file.save(os.path.join(UPLOAD_FOLDER, filename))
          archivos_guardados[campo] = filename
        else:
          archivos_guardados[campo] = None

      cursor.execute(
          '''
            INSERT INTO atencion_instituciones (folio, nombre_escuela, cct, solicitud, plan)
            VALUES (?, ?, ?, ?, ?)
        ''',
          (
              nuevo_folio,
              nombre_escuela,
              cct,
              archivos_guardados['solicitud'],
              archivos_guardados['plan'],
          ),
      )
      conn.commit()
      conn.close()
      return redirect(
          url_for(
              'detalle_area', area_nombre='Atención a instituciones educativas'
          )
      )

  busqueda = request.args.get('q', '').strip()
  if busqueda:
    cursor.execute(
        'SELECT * FROM atencion_instituciones WHERE nombre_escuela LIKE ? OR'
        ' cct LIKE ? OR folio LIKE ?',
        (f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%'),
    )
  else:
    cursor.execute('SELECT * FROM atencion_instituciones')

  filas = cursor.fetchall()
  conn.close()

  instituciones = []
  for row in filas:
    instituciones.append({
        'folio': row['folio'],
        'nombre_escuela': row['nombre_escuela'],
        'cct': row['cct'],
        'archivos': {'solicitud': row['solicitud'], 'plan': row['plan']},
    })

  return render_template(
      'atencion_instituciones.html',
      instituciones=instituciones,
      busqueda=busqueda,
  )


def eliminar_doc_institucional_individual(folio, campo):
  inicializar_db_atencion_instituciones()
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  campos_validos = ['solicitud', 'plan']
  if campo in campos_validos:
    cursor.execute(
        f'SELECT {campo} FROM atencion_instituciones WHERE folio = ?', (folio,)
    )
    row = cursor.fetchone()
    if row and row[0]:
      path_archivo = os.path.join(UPLOAD_FOLDER, row[0])
      if os.path.exists(path_archivo):
        os.remove(path_archivo)
      cursor.execute(
          f'UPDATE atencion_instituciones SET {campo} = NULL WHERE folio = ?',
          (folio,),
      )
      conn.commit()

  conn.close()
  return redirect(
      url_for(
          'detalle_area', area_nombre='Atención a instituciones educativas'
      )
  )