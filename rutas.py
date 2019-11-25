from funciones_basededatos import * #importamos funciones BD
#from modelos import * #importamos las clases que representan nuestras tablas en la BD
#from flask import request#,render_template,flash,redirect,url_for
from formularios import * #importa todos los formularios
import datetime #importar funciones de fecha
from werkzeug.utils import secure_filename #Importa seguridad nombre de archivo
import os.path #importar para funciones de sistema
from random import randint #importa funcion random que sera utilizada para guardar imagen
from app import app,db,login_manager #importa base de datos, app flask y la de login_manager
from funciones_mail import *
from flask_login import login_required, login_user, logout_user, current_user,LoginManager
from sqlalchemy.exc import SQLAlchemyError #se importa para poder trabajar con el error de la base de datos
from errores import * #importando todo
from funciones_mostrar_datos import *

#Función que sobreescribe el método al intentar ingresar a una ruta no autorizada
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Debe iniciar sesión para continuar.','warning')
    #Redireccionar a la página que contiene el formulario de login
    return redirect(url_for('pagina'))


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
            usuario=crearUsuario(formulario.nombre.data,formulario.apellido.data,formulario.email.data,formulario.password.data) #Llama a la función de la base para cargarla a la misma
            login_user(usuario, True)
            if usuario==False:
                return render_template('500.html')
            email=formulario.email.data
            enviarMail(email, 'Bienvenido a MasterEventos', 'mensaje', formulario=formulario)
            return redirect(url_for('pagina')) #Redirecciona a la función index
        else:
            flash('Existe una cuenta registrada con el email ingresado', 'danger')

    return render_template('formulario_registrarse.html', formulario_ingreso=formulario_ingreso,formulario = formulario)


#Función crear evento, permite al usuario crear un evento
@app.route('/crear-evento', methods=["POST", "GET"])
@login_required
def crear_evento():
    formulario_ingreso=Inicio() #Instanciar formulario de inicio
    formulario_crear = CrearEvento() #Instanciar formulario de CrearEvento
    if formulario_crear.validate_on_submit(): #Si el formulario ha sido enviado y es validado correctamente
        f = formulario_crear.imagen.data #Obtener imagen
        filename = secure_filename(formulario_crear.titulo.data + " imagen" + str(randint(1, 2000))) #Modifica el nombre del archivo a uno seguro
        f.save(os.path.join('static/imagenes/', filename)) #Guardar imagen en sistema
        flash('Evento Creado Exitosamente') #Mostrar mensaje
        mostrar_datos_crear(formulario_crear)  #Imprimir datos por consola
        evento=crearEvento(formulario_crear.titulo.data,formulario_crear.fechaEven.data,formulario_crear.hora.data,formulario_crear.opciones.data,filename,
                    formulario_crear.descripcion.data,current_user.usuarioId) #Llama a la función crear evento para que el user lo cree
        if evento == False:
            return render_template('500.html')
        return redirect(url_for('pagina')) #Redirecciona a la función pagina
    return render_template('creacion_evento.html', formulario_crear = formulario_crear, destino = "crear_evento",
                            formulario_ingreso=formulario_ingreso) #Utiliza el template de crear evento


#Función que permite actualizar el evento, ya sea admin o user
@app.route('/actualizar-evento/<id>', methods=["POST","GET"])
@login_required
def actualizar_evento(id):
    formulario_ingreso=Inicio() #Instanciar formulario ingreso
    evento=db.session.query(Evento).filter(Evento.eventoId == id).first_or_404() #consulta
    if current_user.usuarioId == evento.usuarioId:  # Si el usuario tratando de acceder es dueño del evento
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
            evento=actualizarEvento(evento)
            if evento == False:
                return render_template('500.html')
            mostrar_datos_crear(formulario_crear)
            return redirect(url_for('pagina'))
        else: #sino es validado (cuando el user lo modifica)

                formulario_crear.titulo.data=evento.nombre
                formulario_crear.fechaEven.data= evento.fecha
                formulario_crear.hora.data=evento.hora
                formulario_crear.opciones.data=evento.tipo
                formulario_crear.imagen.data=evento.imagen
                formulario_crear.descripcion.data=evento.descripcion
                if evento.aprobado==True: # cuando el evento es modificado vuelve a desaprobarse para que el admin lo vuelva a aprobar
                    evento=db.session.query(Evento).get(id)
                    evento.aprobado=False
                    actualizarEvento(evento)
        return render_template('creacion_evento.html',  formulario_crear=formulario_crear,formulario_ingreso=formulario_ingreso,
                                destino = "actualizar_evento",evento=evento)
    else:
        return redirect(url_for('pagina'))


#Función de Pagina, muestra los eventos traido de la base
@app.route('/', methods=["POST", "GET"])
@app.route('/<int:pag>', methods=["POST", "GET"])
#Ruta a la que se ingresa cuando se pagina con filtros ya aplicados
@app.route('/index/<int:pag>/<fecha_desde>/<fecha_hasta>/<opciones>',methods=['GET'])
def pagina(pag=1, fecha_desde='', fecha_hasta='', opciones=''):
    formulario_ingreso= Inicio() #Instanciar form inicio

    if formulario_ingreso.validate_on_submit(): #si el form ha sido enviado y validado correctamente
        usuario=Usuario.query.filter_by(email=formulario_ingreso.email.data).first()
        if usuario is not None and usuario.verificar_pass(formulario_ingreso.password.data):
        #Loguear Usuario
                login_user(usuario,False)
                user_name=formulario_ingreso.email.data
                flash('Welcome to MasterEventos {}'.format(user_name)) #muestra mensaje
                mostrar_datos_inicio(formulario_ingreso) #mostrar datos
                return redirect(url_for('pagina')) #redirecciona a la funcion pagina
        else:
            #Mostrar error de autentiación
            flash('Email o Contraseña incorrectas', 'succes')
            return redirect(url_for('pagina'))
    filtro=Filtro() #instanciar form filtro
    pag_tam = 6
     #Si se realiza la búsqueda por formulario de filtro
    if(request.args): #el request obtenemos los argumentos que pasamos en el formulario, si no coincide el primer devuelve NONE
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
        eventos=eventos.filter(Evento.tipo==opciones) #va filtrar por opciones
    eventos=eventos.order_by(Evento.fecha.desc()) #trae los eventos recientes primero
    eventos=eventos.paginate(pag,pag_tam,error_out=False) #consulta de la paginación, se le pasa el tamaño de la cantidad de eventos por pagina

    return render_template('pagina_principal.html',formulario_ingreso=formulario_ingreso,
                            filtro=filtro,eventos=eventos)


#Función panel eventos usuario, permite elimanr eventos y verlos detalladamente
@app.route('/mis-eventos-usuario')
@login_required
def mis_eventos_usuario():
    formulario_ingreso=Inicio() #instanciar form inicio
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==current_user.usuarioId).all() #consulta,trae todos los eventos del user
    return render_template('mis_eventos_usuario.html',formulario_ingreso=formulario_ingreso, listaeventos=listaeventos)

#Función que permite ver el evento detallo por parte del user
@app.route('/userevento/<id>', methods=["POST","GET"])

def ver_evento(id):
    formulario_ingreso = Inicio() #instanciar form inicio
    evento = db.session.query(Evento).filter(Evento.eventoId == id).first_or_404() #consulta
    if evento.aprobado is True or (current_user.is_authenticated and current_user.usuarioId == evento.usuarioId): # Si el evento esta aprobado, o quien lo intenta ver es su dueño
        listacomentarios = db.session.query(Comentario).filter(Comentario.eventoId == id).order_by(Comentario.fechahora).all() #consulta, trae el evento por id con todos sus comentarios
        formulario_comentario = Comentarios() #instanciar form comentario
        if formulario_comentario.is_submitted(): #si el form es enviado correctamente
            mostrar_datos_comentario(formulario_comentario) #mostrar datos form
            comentario=crearComentario(formulario_comentario.campocomentario.data,id,current_user.usuarioId) #llama a la funcion crear comentario para que el user lo cree
            if comentario==False:
                return render_template('500.html')
            return redirect(url_for('ver_evento', id=id))#redirecciona a la misma función
        return render_template('evento.html', formulario_comentario=formulario_comentario, id=id, evento=evento,
                                formulario_ingreso=formulario_ingreso, listacomentarios=listacomentarios) #Muestra el template
    else:
        return redirect(url_for('pagina'))

#Función que le permite ver al admin un evento en particular
@app.route('/evento-admin/<id>')
@login_required
def ver_evento_admin(id):
    if current_user.is_admin()==False:
        return redirect(url_for('pagina'))
    formulario_ingreso=Inicio() #instanciar form inicio
    if current_user.is_admin():
        formulario_comentario=Comentarios()
        evento = db.session.query(Evento).filter(Evento.eventoId == id).first_or_404() #trae el evento por id
        listacomentarios = db.session.query(Comentario).filter(Comentario.eventoId == id).order_by(Comentario.fechahora).all() #trae todos los comentarios del evento por id
        return render_template('evento_admin.html',formulario_ingreso=formulario_ingreso, id=id,evento=evento,listacomentarios=listacomentarios,formulario_comentario=formulario_comentario)
    elif not current_user.is_admin():
        return redirect(url_for('pagina'))


#Función que permite al admin tener un panel y saber que eventos estan pendientes de aprobar
@app.route('/eventos-admin')
@login_required
def panel_admin():
    if current_user.is_admin()==False:
        return redirect(url_for('pagina'))
    formulario_ingreso=Inicio() #Instanciar form inicio
    eventos_aprobados= db.session.query(Evento).filter(Evento.aprobado==True).all() #trae todos los eventos aprobados
    eventos_pendientes= db.session.query(Evento).filter(Evento.aprobado==False).all() #trae todos los eventos pendientes de aprobación
    return render_template('mis_eventos_admin.html',eventos_aprobados=eventos_aprobados,eventos_pendientes=eventos_pendientes, formulario_ingreso=formulario_ingreso)

#Funciones BASE DE DATOS

#Función que permite al admin aprobar eventos
@app.route('/evento-admin/aprobar/<id>')
def aprobar_evento(id):
    if current_user.is_admin()==False:
        return redirect(url_for('pagina'))
    evento=db.session.query(Evento).get(id)
    evento.aprobado=True
    email=evento.usuario.email
    enviarMail(email, 'Evento Aprobado por el Admin', 'evento_aprobado')
    actualizarEvento(evento) #actualizar evento para pasar a estado aprobado
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en aprobar_evento en rutas.py")
        return render_template('500.html')
    flash('Evento Aprobado')
    return redirect(url_for('panel_admin',evento=evento))

#Función que permite al admin eliminar los eventos
@app.route('/evento-admin/eliminar/<id>')
def eliminar_evento_admin(id):
    if current_user.is_admin()==False:
        return redirect(url_for('pagina'))
    evento=db.session.query(Evento).get(id) #trae evento por id
    db.session.delete(evento)
    try:
        db.session.commit()
        flash('Evento Eliminado por el Admin')
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en eliminar_evento_admin en rutas.py")

        return render_template('500.html')
    return redirect(url_for('panel_admin',evento=evento))

#Función que permite eliminar Evento por id
@app.route('/evento/eliminar/<id>')
@login_required
def eliminar_evento_usuario(id):
    evento= db.session.query(Evento).get(id) #trae evento por id
    #Eliminar de la db
    db.session.delete(evento)
    #Hacer commit de los cambios
    try:
        db.session.commit()
        flash('Evento Eliminado por el user')
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en eliminarEvento en rutas.py")
        return render_template('500.html')
    return redirect(url_for('mis_eventos_usuario'))

#Función que permite al admin eliminar comentario
@app.route('/comentario/eliminar/<id>')
def eliminar_comentario_admin(id):
    if current_user.is_admin()==False:
        return redirect(url_for('pagina'))
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
        return render_template('500.html')
    flash('EL comentario ha sido borrado con Éxito')
    return redirect(url_for('ver_evento_admin',id=eventoID))

@app.route('/comentario/eliminar/usuario/<id>')
@login_required
def eliminar_comentario_usuario(id):
    comentario = db.session.query(Comentario).get(id) #trae el comentario por id
    eventoID= comentario.eventoId #obtengo el eventoID
    db.session.delete(comentario) #Elimino el comentario
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        #sino queres guardar nada
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en eliminar_comentario_usuario en rutas.py")
        return render_template('500.html')
    flash('El comentario ha sido borrado')
    return redirect(url_for('ver_evento',id=eventoID))
