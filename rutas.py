from funciones import *
from modelos import *
from flask import Flask
from flask import request #en filtro se usa
from flask import render_template #importar templates
from flask import flash #importar para mostrar mensajes flash
from flask import redirect, url_for #importar para permitir redireccionar y generar url
from clases import Registro #importar clase de formulario
from clases import CrearEvento, Comentarios, Inicio, Filtro
import datetime #importar funciones de fecha
from werkzeug.utils import secure_filename #Importa seguridad nombre de archivo
import os.path #importar para funciones de sistema
from random import randint #importa funcion random que sera utilizada para guardar imagen
from app import app,db,login_manager #importa base de datos
from funciones_mail import *
from flask_login import login_required, login_user, logout_user, current_user,LoginManager
from sqlalchemy.exc import SQLAlchemyError
from errores import escribir_log

#Función que sobreescribe el método al intentar ingresar a una ruta no autorizada
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Debe iniciar sesión para continuar.','warning')
    #Redireccionar a la página que contiene el formulario de login
    return redirect(url_for('pagina'))



app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') #clave secreta





#Funciones que muestras los datos obtenidos del envío de formularios
def mostrar_datos(formulario):
    print(formulario.nombre.data)
    print(formulario.apellido.data)
    print(formulario.password.data)
    print(formulario.email.data)
def mostrar_datos_crear(formulario_crear):
    print(formulario_crear.titulo.data)
    print(formulario_crear.fechaEven.data)
    print(formulario_crear.hora.data)
    print(formulario_crear.opciones.data)
    print(formulario_crear.imagen.data)
    print(formulario_crear.descripcion.data)
def mostrar_datos_inicio(formulario_ingreso):
    print(formulario_ingreso.email.data)
    print(formulario_ingreso.password.data)

def mostrar_datos_comentario(formulario_comentario):
    print(formulario_comentario.campocomentario.data)

def mostrar_datos_filtro(filtro):
    print(filtro.opciones.data)


#Logout
@app.route('/logout')
#Limitar el acceso a los usuarios registrados
@login_required
def logout():
    logout_user()
    #Insntanciar formulario de Login
    formulario_ingreso = Inicio()
    filtro=Filtro()
    return redirect(url_for('pagina'))
    #listaeventos=eventos_listar()
    return render_template('pagina_principal.html', formulario_ingreso=formulario_ingreso,filtro=filtro)#eventos=listaeventos)


#Funcion registro, permite que el usuario se registre
#Si obtiene datos por POST muestra los datos por consola y redirecciona mostrando un mensajes
#Si no obtiene datos muestra el formulario

@app.route('/registro', methods=["POST","GET"])
def registro():
    formulario = Registro() #Instanciar formulario de registro
    formulario_ingreso=Inicio() #Instanciar el formulario de inicio
    if formulario.submit1.data is True and formulario.validate_on_submit(): #Si el formulario ha sido enviado y es validado correctamente
        if validar_mailExistente(formulario.email.data):
            flash('Cuenta creada correctamente', 'success') #Mostrar mensaje
            mostrar_datos(formulario)  #Imprimir datos por consola
            crearUsuario(formulario.nombre.data,formulario.apellido.data,formulario.email.data,formulario.password.data) #Llama a la función de la base para cargarla a la misma
            email=formulario.email.data
            enviarMail(email, 'Bienvenido a MasterEventos', 'mensaje', formulario=formulario)
            print(formulario.email.data)
            return redirect(url_for('pagina')) #Redirecciona a la función index
        else:
            flash('Existe una cuenta registrada con el email ingresado', 'danger')

    return render_template('formulario_registrarse.html', formulario_ingreso=formulario_ingreso,formulario = formulario)


#Función crear evento, permite al usuario crear un evento
@app.route('/crear-evento', methods=["POST", "GET"])
@login_required
def crearevento():
    formulario_ingreso=Inicio() #Instanciar formulario de inicio
    formulario_crear = CrearEvento() #Instanciar formulario de CrearEvento
    if formulario_crear.validate_on_submit(): #Si el formulario ha sido enviado y es validado correctamente
        f = formulario_crear.imagen.data #Obtener imagen
        filename = secure_filename(formulario_crear.titulo.data + " imagen" + str(randint(1, 2000))) #Modifica el nombre del archivo a uno seguro
        f.save(os.path.join('static/imagenes/', filename)) #Guardar imagen en sistema
        flash('Evento Creado Exitosamente') #Mostrar mensaje
        mostrar_datos_crear(formulario_crear)  #Imprimir datos por consola
        crearEvento(formulario_crear.titulo.data,formulario_crear.fechaEven.data,formulario_crear.hora.data,formulario_crear.opciones.data,filename,
                    formulario_crear.descripcion.data,current_user.usuarioId) #Llama a la función crear evento para que el user lo cree
        print(filename)
        return redirect(url_for('pagina')) #Redirecciona a la función pagina
    return render_template('creacion_evento.html', formulario_crear = formulario_crear, destino = "crearevento",
                            formulario_ingreso=formulario_ingreso) #Utiliza el template de crear evento


#Función que permite actualizar el evento, ya sea admin o user
@app.route('/actualizar-evento/<id>', methods=["POST","GET"])
@login_required
def actualizar(id):
    formulario_ingreso=Inicio() #Instanciar formulario ingreso
    evento=db.session.query(Evento).get(id) #consulta
    formulario_crear=CrearEvento(obj=evento) #crear un objeto
    CrearEvento.opcional(formulario_crear.imagen) #imagen opcional
    if formulario_crear.validate_on_submit(): #si el form es validado correctamente y ha sido enviado
        flash('Evento Actualizado Correctamente')
        evento.nombre=formulario_crear.titulo.data
        evento.fecha=formulario_crear.fechaEven.data
        evento.hora=formulario_crear.hora.data
        evento.tipo=formulario_crear.opciones.data
        evento.imagen=formulario_crear.imagen.data
        evento.descripcion=formulario_crear.descripcion.data
        actualizarEvento(evento)
        mostrar_datos_crear(formulario_crear)
        return redirect(url_for('pagina'))
        print(evento.nombre)
        print(evento.tipo)
    else: #sino es validado

            formulario_crear.titulo.data=evento.nombre
            formulario_crear.fechaEven.data= evento.fecha
            formulario_crear.hora.data=evento.hora
            formulario_crear.opciones.data=evento.tipo
            formulario_crear.imagen.data=evento.imagen
            formulario_crear.descripcion.data=evento.descripcion
    return render_template('creacion_evento.html',  formulario_crear=formulario_crear,formulario_ingreso=formulario_ingreso,
                            destino = "actualizar",evento=evento)


#Función de Pagina, muestra los eventos traido de la base
@app.route('/', methods=["POST", "GET"])
@app.route('/<int:pag>', methods=["POST", "GET"])
#Ruta a la que se ingresa cuando se pagina con filtros ya aplicados
@app.route('/index/<int:pag>/<fecha_desde>/<fecha_hasta>/<opciones>',methods=['GET'])
def pagina(pag=1, fecha_desde='', fecha_hasta='', opciones=''):
    #listaeventos=eventos_listar() #llama a la funcion que trae los eventos de la base y los guarda en listaeventos
    formulario_ingreso= Inicio() #Instanciar form inicio

    if formulario_ingreso.validate_on_submit(): #si el form ha sido enviado y validado correctamente
        usuario=Usuario.query.filter_by(email=formulario_ingreso.email.data).first()
        if usuario is not None and usuario.verificar_pass(formulario_ingreso.password.data):
        #Loguear Usuario
                login_user(usuario,False)
                user_name=formulario_ingreso.email.data
                flash('Usuario Ingresado Correctamente', format(user_name)) #muestra mensaje
                mostrar_datos_inicio(formulario_ingreso) #mostrar datos
                return redirect(url_for('pagina')) #redirecciona a la funcion pagina
        else:
            #Mostrar error de autentiación
            flash('Email o Contraseña incorrectas', 'succes')
            return redirect(url_for('pagina'))
    filtro=Filtro() #instanciar form filtro
    pag_tam = 6
     #Si se realiza la búsqueda por formulario de filtro
    if(request.args):
        fecha_desde= request.args.get('fecha_desde',None)
        fecha_hasta = request.args.get('fecha_hasta',None)
        opciones = request.args.get('opciones',None)
    eventos = Evento.query.filter(Evento.aprobado==True)
    #Si se filtra por fecha desde cargar el valor en el formulario convirtiendo el valor de string a fecha
    if(fecha_desde!=None and fecha_desde!=''):
        filtro.fecha_desde.data = datetime.datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        eventos=eventos.filter(Evento.fecha>=fecha_desde)
    #Si se filtra por fecha hasta cargar el valor en el formulario convirtiendo el valor de string a fecha
    if(fecha_hasta!=None and fecha_hasta!=''):
        filtro.fecha_hasta.data = datetime.datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
        eventos=eventos.filter(Evento.fecha<=fecha_hasta)
    #Si se filtra por categoria desde cargar el valor en el formulario
    if(opciones!=None and opciones!=''  and opciones!='null' and opciones!='None'):
        filtro.opciones.data = opciones
        eventos=eventos.filter(Evento.tipo==opciones)
    eventos=eventos.order_by(Evento.fecha.desc())
    eventos=eventos.paginate(pag,pag_tam,error_out=False)

    return render_template('pagina_principal.html',formulario_ingreso=formulario_ingreso,
                            filtro=filtro,eventos=eventos)


#Función panel eventos usuario, permite elimanr eventos y verlos detalladamente
@app.route('/mis-eventos-usuario')
@login_required
def miseventos():
    formulario_ingreso=Inicio() #instanciar form inicio
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==current_user.usuarioId).all() #consulta
    return render_template('mis_eventos_usuario.html',formulario_ingreso=formulario_ingreso, listaeventos=listaeventos)

#Función que permite ver el evento detallo por parte del user
@app.route('/userevento/<id>', methods=["POST","GET"])
#@login_required
def evento(id):
    formulario_ingreso = Inicio() #instanciar form inicio
    evento = db.session.query(Evento).filter(Evento.eventoId == id).one() #consulta
    listacomentarios = db.session.query(Comentario).filter(Comentario.eventoId == id).order_by(Comentario.fechahora).all() #consulta
    formulario_comentario = Comentarios() #instanciar form comentario
    if formulario_comentario.is_submitted(): #si el form es enviado correctamente
        mostrar_datos_comentario(formulario_comentario) #mostrar datos form
        crear_comentario=crearComentario(formulario_comentario.campocomentario.data,id,current_user.usuarioId) #llama a la funcion crear comentario para que el user lo cree
        return redirect(url_for('evento', id=id)) #redirecciona a la misma función
    return render_template('evento.html', formulario_comentario=formulario_comentario, id=id, evento=evento,
                            formulario_ingreso=formulario_ingreso, listacomentarios=listacomentarios) #Muestra el template

#Función que le permite ver al admin un evento en particular
@app.route('/evento-admin/<id>')
@login_required
def user_admin(id):
    if current_user.is_admin()==False:
        return redirect(url_for('pagina'))
    formulario_ingreso=Inicio() #instanciar form inicio
    evento = db.session.query(Evento).filter(Evento.eventoId == id).one() #consulta
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==current_user.usuarioId).all() #consulta
    listacomentarios = db.session.query(Comentario).filter(Comentario.eventoId == id).order_by(Comentario.fechahora).all() #consulta
    return render_template('evento_admin.html',formulario_ingreso=formulario_ingreso, id=id,evento=evento,listacomentarios=listacomentarios)

#Función que permite al admin tener un panel y saber que eventos estan pendientes de aprobar
@app.route('/eventos-admin')
@login_required
def aprobareventos():
    if current_user.is_admin()==False:
        return redirect(url_for('pagina'))
    formulario_ingreso=Inicio() #Instanciar form inicio
    eventos_aprobados= db.session.query(Evento).filter(Evento.aprobado==True).all() #consulta BD
    eventos_pendientes= db.session.query(Evento).filter(Evento.aprobado==False).all() #consulta BD
    return render_template('mis_eventos_admin.html',eventos_aprobados=eventos_aprobados,eventos_pendientes=eventos_pendientes, formulario_ingreso=formulario_ingreso)

#Función que permite al admin aprobar eventos
@app.route('/evento-admin/aprobar/<id>')
def aprobar_evento(id):
    evento=db.session.query(Evento).get(id)
    evento.aprobado=True
    email=evento.usuario.email
    enviarMail(email, 'Evento Aprobado por el Admin', 'evento_aprobado')
    actualizarEvento(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en aprobar_evento en rutas.py")
    flash('Evento Aprobado')
    return redirect(url_for('aprobareventos',evento=evento))

#Función que permite al admin eliminar los eventos
@app.route('/evento-admin/eliminar/<id>')
def eliminar_evento_admin(id):
    evento=db.session.query(Evento).get(id)
    db.session.delete(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en eliminar_evento_admin en rutas.py")
    return redirect(url_for('aprobareventos',evento=evento))

#Función que permite eliminar Evento por id
@app.route('/evento/eliminar/<id>')
def eliminarEvento(id):
    evento= db.session.query(Evento).get(id)
    #Eliminar de la db
    db.session.delete(evento)
    #Hacer commit de los cambios
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en eliminarEvento en rutas.py")
    return redirect(url_for('miseventos'))

#Función que permite al admin eliminar comentario
@app.route('/comentario/eliminar/<id>')
def eliminarComentario(id):
    #Obtener comentario por id
    comentario = db.session.query(Comentario).get(id)
    eventoID=comentario.eventoId
    #Eliminar de la db
    db.session.delete(comentario)
    #Hacer commit de los cambios
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en eliminarComentario en rutas.py")
    flash('EL comentario ha sido borrado con Éxito')
    return redirect(url_for('user_admin',id=eventoID))
@app.route('/error')
def error_1():
    return render_template('500.html')
