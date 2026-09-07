import os
import sqlite3
from flask import redirect, render_template, request, session, url_for

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'dif_tecamac.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')


def inicializar_db_servicio():
  if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicio_social (
            folio TEXT PRIMARY KEY,
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


def generar_siguiente_folio():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('SELECT COUNT(*) FROM servicio_social')
  total = cursor.fetchone()[0]
  conn.close()
  siguiente_numero = total + 1
  return f'SS-2026-{siguiente_numero:04d}'


def registrar_servicio_social():
  inicializar_db_servicio()
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  # Eliminar expediente completo por folio
  if request.method == 'POST' and 'eliminar_folio' in request.form:
    folio_a_eliminar = request.form.get('eliminar_folio')
    cursor.execute(
        'SELECT carta, doc_curp, domicilio, foto, aceptacion, bitacora,'
        ' termino FROM servicio_social WHERE folio = ?',
        (folio_a_eliminar,),
    )
    row = cursor.fetchone()
    if row:
      campos_archivos = [
          'carta',
          'doc_curp',
          'domicilio',
          'foto',
          'aceptacion',
          'bitacora',
          'termino',
      ]
      for campo in campos_archivos:
        archivo = row[campo]
        if archivo:
          path_archivo = os.path.join(UPLOAD_FOLDER, archivo)
          if os.path.exists(path_archivo):
            os.remove(path_archivo)

    cursor.execute(
        'DELETE FROM servicio_social WHERE folio = ?', (folio_a_eliminar,)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('detalle_servicio_social'))

  if request.method == 'POST':
    folio_existente = request.form.get('folio_prestador')
    actualizar_campo = request.form.get('actualizar_campo')

    # Reemplazar o subir documento individual usando el folio
    if folio_existente and actualizar_campo:
      file_key = f'file_{actualizar_campo}'
      if file_key in request.files:
        file = request.files[file_key]
        if file and file.filename != '':
          filename = f'{folio_existente}_{actualizar_campo}_{file.filename}'
          file.save(os.path.join(UPLOAD_FOLDER, filename))

          cursor.execute(
              f'SELECT {actualizar_campo} FROM servicio_social WHERE folio = ?',
              (folio_existente,),
          )
          old_file = cursor.fetchone()[0]
          if old_file:
            old_path = os.path.join(UPLOAD_FOLDER, old_file)
            if os.path.exists(old_path):
              os.remove(old_path)

          cursor.execute(
              f'UPDATE servicio_social SET {actualizar_campo} = ? WHERE folio'
              ' = ?',
              (filename, folio_existente),
          )
          conn.commit()
      conn.close()
      return redirect(url_for('detalle_servicio_social'))

    # Registrar nuevo prestador con folio automático
    nombre = request.form.get('nombre')
    curp = request.form.get('curp')

    if nombre and curp:
      nuevo_folio = generar_siguiente_folio()

      nombres_form = [
          'file_carta',
          'file_doc_curp',
          'file_domicilio',
          'file_foto',
          'file_aceptacion',
          'file_bitacora',
          'file_termino',
      ]
      db_campos = [
          'carta',
          'doc_curp',
          'domicilio',
          'foto',
          'aceptacion',
          'bitacora',
          'termino',
      ]

      archivos_guardados = {}
      for campo_db, campo_form in zip(db_campos, nombres_form):
        file = request.files.get(campo_form)
        if file and file.filename != '':
          filename = f'{nuevo_folio}_{campo_db}_{file.filename}'
          file.save(os.path.join(UPLOAD_FOLDER, filename))
          archivos_guardados[campo_db] = filename
        else:
          archivos_guardados[campo_db] = None

      cursor.execute(
          '''
            INSERT INTO servicio_social (folio, nombre, curp, carta, doc_curp, domicilio, foto, aceptacion, bitacora, termino)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
          (
              nuevo_folio,
              nombre,
              curp,
              archivos_guardados['carta'],
              archivos_guardados['doc_curp'],
              archivos_guardados['domicilio'],
              archivos_guardados['foto'],
              archivos_guardados['aceptacion'],
              archivos_guardados['bitacora'],
              archivos_guardados['termino'],
          ),
      )
      conn.commit()
      conn.close()
      return redirect(url_for('detalle_servicio_social'))

  busqueda = request.args.get('q', '').strip()
  if busqueda:
    cursor.execute(
        'SELECT * FROM servicio_social WHERE nombre LIKE ? OR curp LIKE ? OR'
        ' folio LIKE ?',
        (f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%'),
    )
  else:
    cursor.execute('SELECT * FROM servicio_social')

  filas = cursor.fetchall()
  conn.close()

  prestadores = []
  for row in filas:
    prestadores.append({
        'folio': row['folio'],
        'nombre': row['nombre'],
        'curp': row['curp'],
        'archivos': {
            'carta': row['carta'],
            'doc_curp': row['doc_curp'],
            'domicilio': row['domicilio'],
            'foto': row['foto'],
            'aceptacion': row['aceptacion'],
            'bitacora': row['bitacora'],
            'termino': row['termino'],
        },
    })

  return render_template(
      'servicio_social.html', prestadores=prestadores, busqueda=busqueda
  )


def eliminar_documento_individual(folio, campo):
  inicializar_db_servicio()
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  campos_validos = [
      'carta',
      'doc_curp',
      'domicilio',
      'foto',
      'aceptacion',
      'bitacora',
      'termino',
  ]
  if campo in campos_validos:
    cursor.execute(
        f'SELECT {campo} FROM servicio_social WHERE folio = ?', (folio,)
    )
    row = cursor.fetchone()
    if row and row[0]:
      path_archivo = os.path.join(UPLOAD_FOLDER, row[0])
      if os.path.exists(path_archivo):
        os.remove(path_archivo)
      cursor.execute(
          f'UPDATE servicio_social SET {campo} = NULL WHERE folio = ?', (folio,)
      )
      conn.commit()

  conn.close()
  return redirect(url_for('detalle_servicio_social'))