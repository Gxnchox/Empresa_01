import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

# 1. Módulo de Servicio Social
from modulos.servicio_social import (
    inicializar_db_servicio,
    registrar_servicio_social,
    eliminar_documento_individual
)

# 2. Módulos de las demás áreas
from modulos.educacion_inicial import (
    inicializar_db_educacion_inicial,
    registrar_educacion_inicial,
    eliminar_doc_inicial_individual
)
from modulos.educacion_preescolar import (
    inicializar_db_educacion_preescolar,
    registrar_educacion_preescolar,
    eliminar_doc_preescolar_individual
)
from modulos.programas_nutricionales import (
    inicializar_db_programas_nutricionales,
    registrar_programas_nutricionales,
    eliminar_doc_nutricional_individual
)
from modulos.atencion_instituciones import (
    inicializar_db_atencion_instituciones,
    registrar_atencion_instituciones,
    eliminar_doc_institucional_individual
)
from modulos.bibliotecas import (
    inicializar_db_bibliotecas,
    registrar_bibliotecas,
    eliminar_doc_bibliotecas_individual
)

# 3. Módulo de Promoción Artística
from modulos.promocion_artistica import (
    inicializar_db_artistica,
    registrar_promocion_artistica,
    eliminar_documento_artistico_individual
)

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura_dif_tecamac'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Inicialización de bases de datos
os.makedirs(os.path.join(BASE_DIR, 'datos'), exist_ok=True)
inicializar_db_servicio()
inicializar_db_educacion_inicial()
inicializar_db_educacion_preescolar()
inicializar_db_programas_nutricionales()
inicializar_db_atencion_instituciones()
inicializar_db_bibliotecas()
inicializar_db_artistica()

USUARIOS_DEPARTAMENTOS = {
    'Departamento de educación inicial': 'inicial123',
    'Departamento de educación preescolar': 'preescolar123',
    'Departamento de servicio social': 'social123',
    'Departamento de programas nutricionales': 'nutricional123',
    'Atención a instituciones educativas': 'instituciones123',
    'Departamento de bibliotecas': 'bibliotecas123',
    'Departamento de promoción y fomento artístico': 'artistico123'
}

@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('detalle_area', area_nombre=session['usuario']))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        depto = request.form.get('departamento')
        pwd = request.form.get('password')
        if depto in USUARIOS_DEPARTAMENTOS and USUARIOS_DEPARTAMENTOS[depto] == pwd:
            session['usuario'] = depto
            return redirect(url_for('detalle_area', area_nombre=depto))
        return render_template('login.html', error="Contraseña incorrecta", departamentos=USUARIOS_DEPARTAMENTOS.keys())
    
    return render_template('login.html', departamentos=USUARIOS_DEPARTAMENTOS.keys())

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- RUTA UNIFICADA PRINCIPAL POR ÁREA ---
@app.route('/area/<path:area_nombre>', methods=['GET', 'POST'])
def detalle_area(area_nombre):
    if 'usuario' not in session or session['usuario'] != area_nombre:
        return redirect(url_for('login'))

    if area_nombre == 'Departamento de servicio social':
        return registrar_servicio_social()
    elif area_nombre == 'Departamento de educación inicial':
        return registrar_educacion_inicial()
    elif area_nombre == 'Departamento de educación preescolar':
        return registrar_educacion_preescolar()
    elif area_nombre == 'Departamento de programas nutricionales':
        return registrar_programas_nutricionales()
    elif area_nombre == 'Atención a instituciones educativas':
        return registrar_atencion_instituciones()
    elif area_nombre == 'Departamento de bibliotecas':
        return registrar_bibliotecas()
    elif area_nombre == 'Departamento de promoción y fomento artístico':
        return registrar_promocion_artistica()

    return "Área no encontrada", 404

# --- ELIMINAR DOCUMENTO INDIVIDUAL ---
@app.route('/eliminar-documento/<folio>/<campo>', methods=['GET', 'POST'])
def eliminar_doc_individual(folio, campo):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    area = session['usuario']
    if area == 'Departamento de servicio social':
        return eliminar_documento_individual(folio, campo)
    elif area == 'Departamento de educación inicial':
        return eliminar_doc_inicial_individual(folio, campo)
    elif area == 'Departamento de educación preescolar':
        return eliminar_doc_preescolar_individual(folio, campo)
    elif area == 'Departamento de programas nutricionales':
        return eliminar_doc_nutricional_individual(folio, campo)
    elif area == 'Atención a instituciones educativas':
        return eliminar_doc_institucional_individual(folio, campo)
    elif area == 'Departamento de bibliotecas':
        return eliminar_doc_bibliotecas_individual(folio, campo)
    elif area == 'Departamento de promoción y fomento artístico':
        return eliminar_documento_artistico_individual(folio, campo)

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)