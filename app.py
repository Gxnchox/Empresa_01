from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura_dif_tecamac'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Diccionario oficial de departamentos
USUARIOS_DEPARTAMENTOS = {
    'Departamento de educación inicial': 'inicial123',
    'Departamento de educación preescolar': 'preescolar123',
    'Departamento de servicio social': 'social123',
    'Departamento de programas nutricionales': 'nutricional123',
    'Atención a instituciones educativas': 'instituciones123',
    'Departamento de bibliotecas': 'bibliotecas123',
    'Departamento de promoción y fomento artístico': 'artistico123',
}


@app.route('/login', methods=['GET', 'POST'])
def login():
  if 'departamento' in session:
    depto = session['departamento']
    if depto == 'Departamento de servicio social':
      return redirect(url_for('detalle_servicio_social'))
    if depto == 'Departamento de promoción y fomento artístico':
      return redirect(url_for('detalle_promocion_artistica'))
    return redirect(url_for('index'))

  error = None
  if request.method == 'POST':
    departamento = request.form.get('departamento')
    password = request.form.get('password')

    if (
        departamento in USUARIOS_DEPARTAMENTOS
        and USUARIOS_DEPARTAMENTOS[departamento] == password
    ):
      session['departamento'] = departamento
      if departamento == 'Departamento de servicio social':
        return redirect(url_for('detalle_servicio_social'))
      if departamento == 'Departamento de promoción y fomento artístico':
        return redirect(url_for('detalle_promocion_artistica'))
      return redirect(url_for('index'))
    else:
      error = 'Departamento o contraseña incorrectos.'

  return render_template(
      'login.html', departamentos=USUARIOS_DEPARTAMENTOS.keys(), error=error
  )


@app.route('/logout')
def logout():
  session.pop('departamento', None)
  return redirect(url_for('login'))


@app.route('/')
def index():
  if 'departamento' not in session:
    return redirect(url_for('login'))

  depto_actual = session['departamento']
  if depto_actual == 'Departamento de servicio social':
    return redirect(url_for('detalle_servicio_social'))
  if depto_actual == 'Departamento de promoción y fomento artístico':
    return redirect(url_for('detalle_promocion_artistica'))

  return render_template('index.html', departamento=depto_actual)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
  if 'departamento' not in session:
    return redirect(url_for('login'))
  return send_from_directory(UPLOAD_FOLDER, filename)


# --- RUTA PROTEGIDA: SERVICIO SOCIAL ---
@app.route('/area/Departamento de servicio social', methods=['GET', 'POST'])
def detalle_servicio_social():
  if (
      'departamento' not in session
      or session['departamento'] != 'Departamento de servicio social'
  ):
    return redirect(url_for('login'))

  from modulos.servicio_social import registrar_servicio_social

  return registrar_servicio_social()


@app.route('/eliminar-documento/<folio>/<campo>', methods=['POST'])
def eliminar_doc_servicio_social(folio, campo):
  if (
      'departamento' not in session
      or session['departamento'] != 'Departamento de servicio social'
  ):
    return redirect(url_for('login'))

  from modulos.servicio_social import eliminar_documento_individual

  return eliminar_documento_individual(folio, campo)


# --- RUTA PROTEGIDA: PROMOCIÓN Y FOMENTO ARTÍSTICO ---
@app.route(
    '/area/Departamento de promoción y fomento artístico', methods=['GET', 'POST']
)
def detalle_promocion_artistica():
  if (
      'departamento' not in session
      or session['departamento']
      != 'Departamento de promoción y fomento artístico'
  ):
    return redirect(url_for('login'))

  from modulos.promocion_artistica import registrar_promocion_artistica

  return registrar_promocion_artistica()


@app.route('/eliminar-doc-artistico/<folio>/<campo>', methods=['POST'])
def eliminar_doc_artistico(folio, campo):
  if (
      'departamento' not in session
      or session['departamento']
      != 'Departamento de promoción y fomento artístico'
  ):
    return redirect(url_for('login'))

  from modulos.promocion_artistica import eliminar_documento_artistico_individual

  return eliminar_documento_artistico_individual(folio, campo)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)