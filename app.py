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
    registrar_alumno_inicial,
    obtener_alumnos_inicial,
    eliminar_alumno_inicial
)
from modulos.educacion_preescolar import (
    inicializar_db_educacion_preescolar,
    registrar_alumno_preescolar,
    obtener_alumnos_preescolar,
    eliminar_alumno_preescolar
)
from modulos.programas_nutricionales import (
    inicializar_db_programas_nutricionales,
    registrar_beneficiario_nutricional,
    obtener_beneficiarios_nutricionales,
    eliminar_beneficiario_nutricional
)
from modulos.atencion_instituciones import (
    inicializar_db_atencion_instituciones,
    registrar_institucion,
    obtener_instituciones,
    eliminar_institucion
)
from modulos.bibliotecas import (
    inicializar_db_bibliotecas,
    registrar_usuario_biblioteca,
    obtener_usuarios_biblioteca,
    eliminar_usuario_biblioteca
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

# Inicialización de bases de datos
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

def guardar_archivos(request_files):
    guardados = {}
    for key, file in request_files.items():
        if file and file.filename != '':
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            guardados[key] = filename
        else:
            guardados[key] = None
    return guardados

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

# --- RUTA PARA SERVICIO SOCIAL ---
@app.route('/area/Departamento de servicio social', methods=['GET', 'POST'])
def detalle_servicio_social():
    if 'usuario' not in session or session['usuario'] != 'Departamento de servicio social':
        return redirect(url_for('login'))
    return registrar_servicio_social()

@app.route('/area/Departamento de servicio social/eliminar_doc/<folio>/<campo>')
def eliminar_doc_individual(folio, campo):
    if 'usuario' not in session or session['usuario'] != 'Departamento de servicio social':
        return redirect(url_for('login'))
    return eliminar_documento_individual(folio, campo)

# --- RUTA PARA PROMOCIÓN ARTÍSTICA ---
@app.route('/area/Departamento de promoción y fomento artístico', methods=['GET', 'POST'])
def detalle_promocion_artistica():
    if 'usuario' not in session or session['usuario'] != 'Departamento de promoción y fomento artístico':
        return redirect(url_for('login'))
    return registrar_promocion_artistica()

@app.route('/area/Departamento de promoción y fomento artístico/eliminar_doc/<folio>/<campo>')
def eliminar_doc_artistico(folio, campo):
    if 'usuario' not in session or session['usuario'] != 'Departamento de promoción y fomento artístico':
        return redirect(url_for('login'))
    return eliminar_documento_artistico_individual(folio, campo)

# --- RUTA GENERAL PARA LAS DEMÁS ÁREAS ---
@app.route('/area/<area_nombre>')
def detalle_area(area_nombre):
    if 'usuario' not in session or session['usuario'] != area_nombre:
        return redirect(url_for('login'))
    
    if area_nombre == 'Departamento de servicio social':
        return redirect(url_for('detalle_servicio_social'))
    if area_nombre == 'Departamento de promoción y fomento artístico':
        return redirect(url_for('detalle_promocion_artistica'))

    q = request.args.get('q', None)

    if area_nombre == 'Departamento de educación inicial':
        alumnos = obtener_alumnos_inicial(q)
        return render_template('educacion_inicial.html', alumnos=alumnos, busqueda=q)

    elif area_nombre == 'Departamento de educación preescolar':
        alumnos = obtener_alumnos_preescolar(q)
        return render_template('educacion_preescolar.html', alumnos=alumnos, busqueda=q)

    elif area_nombre == 'Departamento de programas nutricionales':
        beneficiarios = obtener_beneficiarios_nutricionales(q)
        return render_template('programas_nutricionales.html', beneficiarios=beneficiarios, busqueda=q)

    elif area_nombre == 'Atención a instituciones educativas':
        inst = obtener_instituciones(q)
        return render_template('atencion_instituciones.html', instituciones=inst, busqueda=q)

    elif area_nombre == 'Departamento de bibliotecas':
        usr = obtener_usuarios_biblioteca(q)
        return render_template('bibliotecas.html', usuarios=usr, busqueda=q)

    return "Área no encontrada", 404

# --- GUARDAR RUTAS PARA ÁREAS GENERALES ---
@app.route('/area/<area_nombre>/guardar', methods=['POST'])
def guardar_registro(area_nombre):
    archivos = guardar_archivos(request.files)

    if area_nombre == 'Departamento de educación inicial':
        nombre = request.form.get('nombre')
        curp = request.form.get('curp')
        registrar_alumno_inicial(nombre, curp, archivos)

    elif area_nombre == 'Departamento de educación preescolar':
        nombre = request.form.get('nombre')
        curp = request.form.get('curp')
        registrar_alumno_preescolar(nombre, curp, archivos)

    elif area_nombre == 'Departamento de programas nutricionales':
        nombre = request.form.get('nombre')
        curp = request.form.get('curp')
        registrar_beneficiario_nutricional(nombre, curp, archivos)

    elif area_nombre == 'Atención a instituciones educativas':
        escuela = request.form.get('nombre_escuela')
        cct = request.form.get('cct')
        registrar_institucion(escuela, cct, archivos)

    elif area_nombre == 'Departamento de bibliotecas':
        nombre = request.form.get('nombre')
        curp = request.form.get('curp')
        registrar_usuario_biblioteca(nombre, curp, archivos)

    return redirect(url_for('detalle_area', area_nombre=area_nombre))

# --- ELIMINAR RUTAS PARA ÁREAS GENERALES ---
@app.route('/area/<area_nombre>/eliminar/<folio>')
def eliminar_registro(area_nombre, folio):
    if area_nombre == 'Departamento de educación inicial':
        eliminar_alumno_inicial(folio)
    elif area_nombre == 'Departamento de educación preescolar':
        eliminar_alumno_preescolar(folio)
    elif area_nombre == 'Departamento de programas nutricionales':
        eliminar_beneficiario_nutricional(folio)
    elif area_nombre == 'Atención a instituciones educativas':
        eliminar_institucion(folio)
    elif area_nombre == 'Departamento de bibliotecas':
        eliminar_usuario_biblioteca(folio)

    return redirect(url_for('detalle_area', area_nombre=area_nombre))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)