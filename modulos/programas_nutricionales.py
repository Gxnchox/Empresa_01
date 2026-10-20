import os
import sqlite3
from flask import redirect, render_template, request, session, url_for

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
            curp_doc TEXT,
            comprobante_domicilio TEXT,
            estudio_socioeconomico TEXT
        )
    ''')
  conn.commit()
  conn.close()


def generar_folio_nutricional():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('SELECT COUNT(*) FROM programas_nutricionales')
  total = cursor.fetchone()[0]
  conn.close()
  return f'PN-2026-{(total + 1):04d}'


def registrar_programas_nutricionales():
  inicializar_db_programas_nutricionales()
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  if request.method == 'POST' and 'eliminar_folio' in request.form:
    folio_a_eliminar = request.form.get('eliminar_folio')
    cursor.execute(
        'SELECT curp_doc, comprobante_domicilio, estudio_socioeconomico FROM'
        ' programas_nutricionales WHERE folio = ?',
        (folio_a_eliminar,),
    )
    row = cursor.fetchone()
    if row:
      campos_archivos = [
          'curp_doc',
          'comprobante_domicilio',
          'estudio_socioeconomico',
      ]
      for campo in campos_archivos:
        archivo = row[campo]
        if archivo:
          path_archivo = os.path.join(UPLOAD_FOLDER, archivo)
          if os.path.exists(path_archivo):
            os.remove(path_archivo)

    cursor.execute(
        'DELETE FROM programas_nutricionales WHERE folio = ?',
        (folio_a_eliminar,),
    )
    conn.commit()
    conn.close()
    return redirect(
        url_for(
            'detalle_area',
            area_nombre='Departamento de programas nutricionales',
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
            f'SELECT {actualizar_campo} FROM programas_nutricionales WHERE'
            ' folio = ?',
            (folio_existente,),
        )
        old_file = cursor.fetchone()[0]
        if old_file:
          old_path = os.path.join(UPLOAD_FOLDER, old_file)
          if os.path.exists(old_path):
            os.remove(old_path)

        cursor.execute(
            f'UPDATE programas_nutricionales SET {actualizar_campo} = ? WHERE'
            ' folio = ?',
            (filename, folio_existente),
        )
        conn.commit()
      conn.close()
      return redirect(
          url_for(
              'detalle_area',
              area_nombre='Departamento de programas nutricionales',
          )
      )

    nombre = request.form.get('nombre')
    curp = request.form.get('curp')

    if nombre and curp:
      nuevo_folio = generar_folio_nutricional()
      db_campos = ['curp_doc', 'comprobante_domicilio', 'estudio_socioeconomico']
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
            INSERT INTO programas_nutricionales (folio, nombre, curp, curp_doc, comprobante_domicilio, estudio_socioeconomico)
            VALUES (?, ?, ?, ?, ?, ?)
        ''',
          (
              nuevo_folio,
              nombre,
              curp,
              archivos_guardados['curp_doc'],
              archivos_guardados['comprobante_domicilio'],
              archivos_guardados['estudio_socioeconomico'],
          ),
      )
      conn.commit()
      conn.close()
      return redirect(
          url_for(
              'detalle_area',
              area_nombre='Departamento de programas nutricionales',
          )
      )

  busqueda = request.args.get('q', '').strip()
  if busqueda:
    cursor.execute(
        'SELECT * FROM programas_nutricionales WHERE nombre LIKE ? OR curp LIKE'
        ' ? OR folio LIKE ?',
        (f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%'),
    )
  else:
    cursor.execute('SELECT * FROM programas_nutricionales')

  filas = cursor.fetchall()
  conn.close()

  beneficiarios = []
  for row in filas:
    beneficiarios.append({
        'folio': row['folio'],
        'nombre': row['nombre'],
        'curp': row['curp'],
        'archivos': {
            'curp_doc': row['curp_doc'],
            'comprobante_domicilio': row['comprobante_domicilio'],
            'estudio_socioeconomico': row['estudio_socioeconomico'],
        },
    })

  return render_template(
      'programas_nutricionales.html',
      beneficiarios=beneficiarios,
      busqueda=busqueda,
  )


def eliminar_doc_nutricional_individual(folio, campo):
  inicializar_db_programas_nutricionales()
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  campos_validos = ['curp_doc', 'comprobante_domicilio', 'estudio_socioeconomico']
  if campo in campos_validos:
    cursor.execute(
        f'SELECT {campo} FROM programas_nutricionales WHERE folio = ?', (folio,)
    )
    row = cursor.fetchone()
    if row and row[0]:
      path_archivo = os.path.join(UPLOAD_FOLDER, row[0])
      if os.path.exists(path_archivo):
        os.remove(path_archivo)
      cursor.execute(
          f'UPDATE programas_nutricionales SET {campo} = NULL WHERE folio = ?',
          (folio,),
      )
      conn.commit()

  conn.close()
  return redirect(
      url_for(
          'detalle_area',
          area_nombre='Departamento de programas nutricionales',
      )
  )