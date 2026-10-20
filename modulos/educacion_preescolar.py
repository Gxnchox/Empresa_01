import os
import sqlite3
from flask import redirect, render_template, request, session, url_for

# Configuración de ruta absoluta unificada para la base de datos en AWS EC2
BASE_DIR = '/home/ubuntu/Empresa_01'
DB_PATH = os.path.join(BASE_DIR, 'dif_tecamac.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


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


def generar_folio_preescolar():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('SELECT COUNT(*) FROM educacion_preescolar')
  total = cursor.fetchone()[0]
  conn.close()
  return f'EP-2026-{(total + 1):04d}'


def registrar_educacion_preescolar():
  inicializar_db_educacion_preescolar()
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  if request.method == 'POST' and 'eliminar_folio' in request.form:
    folio_a_eliminar = request.form.get('eliminar_folio')
    cursor.execute(
        'SELECT acta_nacimiento, curp_doc, comprobante_domicilio,'
        ' certificado_medico, foto, ine_tutor FROM educacion_preescolar WHERE'
        ' folio = ?',
        (folio_a_eliminar,),
    )
    row = cursor.fetchone()
    if row:
      campos_archivos = [
          'acta_nacimiento',
          'curp_doc',
          'comprobante_domicilio',
          'certificado_medico',
          'foto',
          'ine_tutor',
      ]
      for campo in campos_archivos:
        archivo = row[campo]
        if archivo:
          path_archivo = os.path.join(UPLOAD_FOLDER, archivo)
          if os.path.exists(path_archivo):
            os.remove(path_archivo)

    cursor.execute(
        'DELETE FROM educacion_preescolar WHERE folio = ?', (folio_a_eliminar,)
    )
    conn.commit()
    conn.close()
    return redirect(
        url_for(
            'detalle_area',
            area_nombre='Departamento de educación preescolar',
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
            f'SELECT {actualizar_campo} FROM educacion_preescolar WHERE folio ='
            ' ?',
            (folio_existente,),
        )
        old_file = cursor.fetchone()[0]
        if old_file:
          old_path = os.path.join(UPLOAD_FOLDER, old_file)
          if os.path.exists(old_path):
            os.remove(old_path)

        cursor.execute(
            f'UPDATE educacion_preescolar SET {actualizar_campo} = ? WHERE'
            ' folio = ?',
            (filename, folio_existente),
        )
        conn.commit()
      conn.close()
      return redirect(
          url_for(
              'detalle_area',
              area_nombre='Departamento de educación preescolar',
          )
      )

    nombre = request.form.get('nombre')
    curp = request.form.get('curp')

    if nombre and curp:
      nuevo_folio = generar_folio_preescolar()
      db_campos = [
          'acta_nacimiento',
          'curp_doc',
          'comprobante_domicilio',
          'certificado_medico',
          'foto',
          'ine_tutor',
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
            INSERT INTO educacion_preescolar (folio, nombre, curp, acta_nacimiento, curp_doc, comprobante_domicilio, certificado_medico, foto, ine_tutor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
          (
              nuevo_folio,
              nombre,
              curp,
              archivos_guardados['acta_nacimiento'],
              archivos_guardados['curp_doc'],
              archivos_guardados['comprobante_domicilio'],
              archivos_guardados['certificado_medico'],
              archivos_guardados['foto'],
              archivos_guardados['ine_tutor'],
          ),
      )
      conn.commit()
      conn.close()
      return redirect(
          url_for(
              'detalle_area',
              area_nombre='Departamento de educación preescolar',
          )
      )

  busqueda = request.args.get('q', '').strip()
  if busqueda:
    cursor.execute(
        'SELECT * FROM educacion_preescolar WHERE nombre LIKE ? OR curp LIKE ?'
        ' OR folio LIKE ?',
        (f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%'),
    )
  else:
    cursor.execute('SELECT * FROM educacion_preescolar')

  filas = cursor.fetchall()
  conn.close()

  alumnos = []
  for row in filas:
    alumnos.append({
        'folio': row['folio'],
        'nombre': row['nombre'],
        'curp': row['curp'],
        'archivos': {
            'acta_nacimiento': row['acta_nacimiento'],
            'curp_doc': row['curp_doc'],
            'comprobante_domicilio': row['comprobante_domicilio'],
            'certificado_medico': row['certificado_medico'],
            'foto': row['foto'],
            'ine_tutor': row['ine_tutor'],
        },
    })

  return render_template(
      'educacion_preescolar.html', alumnos=alumnos, busqueda=busqueda
  )


def eliminar_doc_preescolar_individual(folio, campo):
  inicializar_db_educacion_preescolar()
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  campos_validos = [
      'acta_nacimiento',
      'curp_doc',
      'comprobante_domicilio',
      'certificado_medico',
      'foto',
      'ine_tutor',
  ]
  if campo in campos_validos:
    cursor.execute(
        f'SELECT {campo} FROM educacion_preescolar WHERE folio = ?', (folio,)
    )
    row = cursor.fetchone()
    if row and row[0]:
      path_archivo = os.path.join(UPLOAD_FOLDER, row[0])
      if os.path.exists(path_archivo):
        os.remove(path_archivo)
      cursor.execute(
          f'UPDATE educacion_preescolar SET {campo} = NULL WHERE folio = ?',
          (folio,),
      )
      conn.commit()

  conn.close()
  return redirect(
      url_for(
          'detalle_area',
          area_nombre='Departamento de educación preescolar',
      )
  )