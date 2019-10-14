from funciones import *
from modelos import *
from flask import Flask
from flask import render_template #importar templates
from flask_wtf import CSRFProtect #importar para proteccion CSRF
from flask import flash #importar para mostrar mensajes flash
from flask import redirect, url_for #importar para permitir redireccionar y generar url
from clases import Registro #importar clase de formulario
from clases import CrearEvento, Comentarios, Inicio, Filtro
import datetime #importar funciones de fecha
from werkzeug.utils import secure_filename #Importa seguridad nombre de archivo
import os.path #importar para funciones de sistema
from random import randint #importa funcion random que sera utilizada para guardar imagen
from app import db #importa base de datos



app=Flask(__name__)

csrf = CSRFProtect(app) #Iniciar protección CSRF
app.secret_key = 'esta_es_la_clave_secreta' #clave secreta

logueado = True
admin =  False

if logueado is True:
    admin = False



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

def mostrar_datos_comentario(formulario_comentario):
    print(formulario_comentario.campocomentario.data)

def mostrar_datos_filtro(filtro):
    print(filtro.opciones.data)



#Funcion registro, permite que el usuario se registre
#Si obtiene datos por POST muestra los datos por consola y redirecciona mostrando un mensajes
#Si no obtiene datos muestra el formulario
@app.route('/registro', methods=["POST","GET"])
def registro():
    formulario = Registro() #Instanciar formulario de registro
    formulario_ingreso=Inicio() #Instanciar el formulario de inicio
    if formulario.validate_on_submit(): #Si el formulario ha sido enviado y es validado correctamente
        flash('Usuario registrado exitosamente') #Mostrar mensaje
        mostrar_datos(formulario)  #Imprimir datos por consola
        crearUsuario(formulario.nombre.data,formulario.apellido.data,formulario.email.data,formulario.password.data) #Llama a la función de la base para cargarla a la misma
        return redirect(url_for('pagina')) #Redirecciona a la función index

    return render_template('formulario_registrarse.html', formulario_ingreso=formulario_ingreso,formulario = formulario, logueado=logueado, admin=admin)


#Función crear evento, permite al usuario crear un evento
@app.route('/crear-evento', methods=["POST", "GET"])
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
                    formulario_crear.descripcion.data,299) #Llama a la función crear evento para que el user lo cree
        print(filename)
        return redirect(url_for('pagina')) #Redirecciona a la función pagina
    return render_template('creacion_evento.html', formulario_crear = formulario_crear, destino = "crearevento",logueado=logueado, admin=admin,
                            formulario_ingreso=formulario_ingreso) #Utiliza el template de crear evento


#Función que permite actualizar el evento, ya sea admin o user
@app.route('/actualizar-evento/<id>', methods=["POST","GET"])
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
    return render_template('creacion_evento.html',  formulario_crear=formulario_crear,logueado=logueado, admin=admin,formulario_ingreso=formulario_ingreso,
                            destino = "actualizar",evento=evento)


#Función de Pagina, muestra los eventos traido de la base
@app.route('/', methods=["POST", "GET"])
def pagina():
    listaeventos=eventos_listar() #llama a la funcion que trae los eventos de la base y los guarda en listaeventos
    formulario_ingreso= Inicio() #Instanciar form inicio
    filtro=Filtro() #instanciar form filtro
    if formulario_ingreso.validate_on_submit(): #si el form ha sido enviado y validado correctamente
        flash('Usuario Ingresado Correctamente') #muestra mensaje
        mostrar_datos_inicio(formulario_ingreso) #mostrar datos
        return redirect(url_for('pagina')) #redirecciona a la funcion pagina
    eventos = db.session.query(Evento).filter(Evento.fecha>= db.session.query(Evento).filter(Evento.aprobado == 1)).order_by(Evento.fecha) #consulta
    if filtro.is_submitted():
        listaeventos= db.session.query(Evento)
        if filtro.fecha_desde.data is not None:
            listaeventos = listaeventos.filter(Evento.fecha >= filtro.fecha_desde.data)
        if filtro.fecha_hasta.data is not None:
            listaeventos = listaeventos.filter(Evento.fecha <= filtro.fecha_hasta.data)
        if filtro.opciones.data != '1':
            listaeventos= listaeventos.filter(Evento.tipo == filtro.opciones.data)

        eventos = listaeventos.filter(Evento.aprobado == 1).order_by(Evento.fecha)
    return render_template('pagina_principal.html',formulario_ingreso=formulario_ingreso,listaeventos=listaeventos,logueado=logueado, admin=admin,
                            filtro=filtro,eventos=eventos)


#Función panel eventos usuario, permite elimanr eventos y verlos detalladamente
@app.route('/mis-eventos-usuario')
def miseventos():
    formulario_ingreso=Inicio() #instanciar form inicio
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==287).all() #consulta
    return render_template('mis_eventos_usuario.html',formulario_ingreso=formulario_ingreso, listaeventos=listaeventos,logueado=logueado, admin=admin)

#Función que permite ver el evento detallo por parte del user
@app.route('/userevento/<id>', methods=["POST","GET"])
def evento(id):
    formulario_ingreso = Inicio() #instanciar form inicio
    evento = db.session.query(Evento).filter(Evento.eventoId == id).one() #consulta
    listacomentarios = db.session.query(Comentario).filter(Comentario.eventoId == id).order_by(Comentario.fechahora).all() #consulta
    formulario_comentario = Comentarios() #instanciar form comentario
    if formulario_comentario.is_submitted(): #si el form es enviado correctamente
        mostrar_datos_comentario(formulario_comentario) #mostrar datos form
        crear_comentario=crearComentario(formulario_comentario.campocomentario.data,id,260) #llama a la funcion crear comentario para que el user lo cree
        return redirect(url_for('evento', id=id)) #redirecciona a la misma función
    return render_template('evento.html', formulario_comentario=formulario_comentario, id=id, evento=evento,
                           logueado=logueado, admin=admin, formulario_ingreso=formulario_ingreso, listacomentarios=listacomentarios) #Muestra el template

#Función que le permite ver al admin un evento en particular
@app.route('/evento-admin/<id>')
def user_admin(id):
    formulario_ingreso=Inicio() #instanciar form inicio
    evento = db.session.query(Evento).filter(Evento.eventoId == id).one() #consulta
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==283).all() #consulta
    listacomentarios = db.session.query(Comentario).filter(Comentario.eventoId == id).order_by(Comentario.fechahora).all() #consulta
    return render_template('evento_admin.html',formulario_ingreso=formulario_ingreso, id=id,evento=evento,listacomentarios=listacomentarios, admin=admin, logueado=logueado)

#Función que permite al admin tener un panel y saber que eventos estan pendientes de aprobar
@app.route('/eventos-admin')
def aprobareventos():
    formulario_ingreso=Inicio() #Instanciar form inicio
    eventos_aprobados= db.session.query(Evento).filter(Evento.aprobado==True).all() #consulta BD
    eventos_pendientes= db.session.query(Evento).filter(Evento.aprobado==False).all() #consulta BD
    return render_template('mis_eventos_admin.html',eventos_aprobados=eventos_aprobados,eventos_pendientes=eventos_pendientes,logueado=logueado, admin=admin, formulario_ingreso=formulario_ingreso)

#Función que permite al admin aprobar eventos
@app.route('/evento-admin/aprobar/<id>')
def aprobar_evento(id):
    evento=db.session.query(Evento).get(id)
    evento.aprobado=True
    actualizarEvento(evento)
    return redirect(url_for('aprobareventos',evento=evento))

#Función que permite al admin eliminar los eventos
@app.route('/evento-admin/eliminar/<id>')
def eliminar_evento_admin(id):
    evento=db.session.query(Evento).get(id)
    db.session.delete(evento)
    db.session.commit()
    return redirect(url_for('aprobareventos',evento=evento))

#Función que permite eliminar Evento por id
@app.route('/evento/eliminar/<id>')
def eliminarEvento(id):
    evento= db.session.query(Evento).get(id)
    #Eliminar de la db
    db.session.delete(evento)
    #Hacer commit de los cambios
    db.session.commit()
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
    db.session.commit()
    flash('EL comentario ha sido borrado con Éxito')
    return redirect(url_for('user_admin',id=eventoID))


app.run(debug=True)
