from app import db,app
from modelos import *
from flask import redirect
from flask import flash #importar para mostrar mensajes flash
from flask_login import login_required, login_user, logout_user, current_user,LoginManager
from sqlalchemy.exc import SQLAlchemyError
from errores import escribir_log

#Función que permite listar los eventos de la BD
def eventos_listar():
    lista_evento=db.session.query(Evento).all()
    return lista_evento



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#RUTAS BASE BD


#Función que permite crear un evento y guardarlo en la base de datos
@app.route('/evento/crear<eventoId>/<nombre>/<fechahora>/<tipo>/<imagen>/<descripcion>/<UsuarioId>')
@login_required
def crearEvento(titulo,fechaEven,hora,tipo,imagen,descripcion,usuarioId):
    usuario=db.session.query(Usuario).get(usuarioId)
    evento = Evento(usuario=usuario,nombre=titulo,fecha=fechaEven,hora=hora,tipo=tipo,imagen=imagen,descripcion=descripcion)
    #Agregar a db
    db.session.add(evento)
    #Hacer commit de los cambios
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en crearEvento en funciones.py")
    #return render_template('evento.html',evento=evento)

#Función que permite actualizar el evento
@app.route('/evento/actualizar/<evento>')
@login_required
def actualizarEvento(evento):
    db.session.add(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(e._message, "error en base de datos en actualizarEvento en funciones.py")




#Función que permite crear comentario
@app.route('/comentario/crear/<eventoId>/<texto>/<fechahora>')
@login_required
def crearComentario(campocomentario,eventoId,usuarioId):
    usuario=db.session.query(Usuario).get(usuarioId)
    evento=db.session.query(Evento).get(eventoId)
    fechahora=db.func.current_timestamp()
    comentario = Comentario(contenido=campocomentario,evento=evento,usuario=usuario)
    #Agregar a db
    db.session.add(comentario)
    try:
    #Hacer commit de los cambios
        db.session.commit()
        flash('Comentario Enviado')
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(e._message, "error en base de datos en crearComentario en funciones.py")


#Función que permite al user registrarse en la BD
@app.route('/usuario/crear/<nombre>/<apellido>/<email>/<password>')
def crearUsuario(nombre,apellido,email,password,admin=False):
    #Crear una persona
    usuario = Usuario(nombre=nombre, apellido=apellido,email=email,passworden=password,admin=admin)
    #Agregar a db
    db.session.add(usuario)
    #Hacer commit de los cambios
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(e._message, "error en base de datos en crearUsuario en funciones.py")

@app.route('/errorbase')
def probar_Error():
    usuario=Usuario()
    db.session.add(usuario)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(e._message, "error en base de datos ")
    return redirect(url_for('pagina'))
