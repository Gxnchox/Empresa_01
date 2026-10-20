import os
import sqlite3
from flask import redirect, render_template, request, session, url_for

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'dif_tecamac.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')


def inicializar_db_artistica():
  if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('''
        CREATE TABLE IF NOT EXISTS promocion_artistica (
            folio TEXT PRIMARY KEY,
            nombre_proyecto TEXT NOT NULL,
            responsable TEXT NOT NULL,
            integrantes TEXT,
            instrumentos TEXT,
            vestuario TEXT,
            lugares TEXT,
            entrevistas TEXT,
            redes TEXT,
            extra TEXT
        )
    ''')
  conn.commit()
  conn.close()


def generar_folio_artistico():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('SELECT COUNT(*) FROM promocion_artistica')
  total = cursor.fetchone()[0]
  conn.close()
  return f'FA-2026-{(total + 1):04d}'


def registrar_promocion_artistica():
  inicializar_db_artistica()
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  if request.method == 'POST' and 'eliminar_folio' in request.form:
    folio_a_eliminar = request.form.get('eliminar_folio')
    cursor.execute(
        'SELECT integrantes, instrumentos, vestuario, lugares, entrevistas,'
        ' redes, extra FROM promocion_artistica WHERE folio = ?',
        (folio_a_eliminar,),
    )
    row = cursor.fetchone()
    if row:
      campos_archivos = [
          'integrantes',
          'instrumentos',
          'vestuario',
          'lugares',
          'entrevistas',
          'redes',
          'extra',
      ]
      for campo in campos_archivos:
        archivo = row[campo]
        if archivo:
          path_archivo = os.path.join(UPLOAD_FOLDER, archivo)
          if os.path.exists(path_archivo):
            os.remove(path_archivo)

    cursor.execute(
        'DELETE FROM promocion_artistica WHERE folio = ?', (folio_a_eliminar,)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('detalle_promocion_artistica'))

  if request.method == 'POST':
    folio_existente = request.form.get('folio_proyecto') or request.form.get(
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
            f'SELECT {actualizar_campo} FROM promocion_artistica WHERE folio ='
            ' ?',
            (folio_existente,),
        )
        old_file = cursor.fetchone()[0]
        if old_file:
          old_path = os.path.join(UPLOAD_FOLDER, old_file)
          if os.path.exists(old_path):
            os.remove(old_path)

        cursor.execute(
            f'UPDATE promocion_artistica SET {actualizar_campo} = ? WHERE'
            ' folio = ?',
            (filename, folio_existente),
        )
        conn.commit()
      conn.close()
      return redirect(url_for('detalle_promocion_artistica'))

    nombre_proyecto = request.form.get('nombre_proyecto')
    responsable = request.form.get('responsable')

    if nombre_proyecto and responsable:
      nuevo_folio = generar_folio_artistico()
      db_campos = [
          'integrantes',
          'instrumentos',
          'vestuario',
          'lugares',
          'entrevistas',
          'redes',
          'extra',
      ]
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
            INSERT INTO promocion_artistica (folio, nombre_proyecto, responsable, integrantes, instrumentos, vestuario, lugares, entrevistas, redes, extra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
          (
              nuevo_folio,
              nombre_proyecto,
              responsable,
              archivos_guardados['integrantes'],
              archivos_guardados['instrumentos'],
              archivos_guardados['vestuario'],
              archivos_guardados['lugares'],
              archivos_guardados['entrevistas'],
              archivos_guardados['redes'],
              archivos_guardados['extra'],
          ),
      )
      conn.commit()
      conn.close()
      return redirect(url_for('detalle_promocion_artistica'))

  busqueda = request.args.get('q', '').strip()
  if busqueda:
    cursor.execute(
        'SELECT * FROM promocion_artistica WHERE nombre_proyecto LIKE ? OR'
        ' responsable LIKE ? OR folio LIKE ?',
        (f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%'),
    )
  else:
    cursor.execute('SELECT * FROM promocion_artistica')

  filas = cursor.fetchall()
  conn.close()

  proyectos = []
  for row in filas:
    proyectos.append({
        'folio': row['folio'],
        'nombre_proyecto': row['nombre_proyecto'],
        'responsable': row['responsable'],
        'archivos': {
            'integrantes': row['integrantes'],
            'instrumentos': row['instrumentos'],
            'vestuario': row['vestuario'],
            'lugares': row['lugares'],
            'entrevistas': row['entrevistas'],
            'redes': row['redes'],
            'extra': row['extra'],
        },
    })

  return render_template(
      'promocion_artistica.html', proyectos=proyectos, busqueda=busqueda
  )


def eliminar_documento_artistico_individual(folio, campo):
  inicializar_db_artistica()
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  campos_validos = [
      'integrantes',
      'instrumentos',
      'vestuario',
      'lugares',
      'entrevistas',
      'redes',
      'extra',
  ]
  if campo in campos_validos:
    cursor.execute(
        f'SELECT {campo} FROM promocion_artistica WHERE folio = ?', (folio,)
    )
    row = cursor.fetchone()
    if row and row[0]:
      path_archivo = os.path.join(UPLOAD_FOLDER, row[0])
      if os.path.exists(path_archivo):
        os.remove(path_archivo)
      cursor.execute(
          f'UPDATE promocion_artistica SET {campo} = NULL WHERE folio = ?',
          (folio,),
      )
      conn.commit()

  conn.close()
  return redirect(url_for('detalle_promocion_artistica'))