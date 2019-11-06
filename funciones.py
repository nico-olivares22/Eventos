from app import db,app
from modelos import *
from flask import Flask, redirect
from flask import flash #importar para mostrar mensajes flash
from flask_login import login_required, login_user, logout_user, current_user,LoginManager
from sqlalchemy.exc import SQLAlchemyError
from errores import escribir_log

#Función que permite lsitar los eventos de la BD
def eventos_listar():
    lista_evento=db.session.query(Evento).all()
    return lista_evento



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#RUTAS BASE BD

#NO se usa
#@app.route('/')
@app.route('/evento/list')
def listarEventos():
    # EJ: persona/list
    eventos = db.session.query(Evento).all()
    return render_template('eventos.html',eventos=eventos,filtro="")

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
        escribir_log(str(e.message()), "Función crearEvento en funciones.py")
    #return render_template('evento.html',evento=evento)

#Función que permite actualizar el evento
@app.route('/evento/actualizar/<evento>')
@login_required
def actualizarEvento(evento):
    db.session.add(evento)
    db.session.commit()

# NO se usa
@app.route('/evento/getById/<id>')
def getEventoById(id):
    # EJ: persona/getById/2
    # Filtra por id
    evento =  db.session.query(Evento).get(id)
    return render_template('evento.html',evento=evento)



#No se usa
def listarComentarios(id):
    # EJ: persona/list
    comentarios = db.session.query(Comentario).filter(Comentario.eventoId == id).all()
    return comentarios

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
    #Hacer commit de los cambios
    db.session.commit()
    flash('Comentario Enviado')
    #return render_template('comentario.html',comentario=comentario)

#NO se usa
@app.route('/comentario/getById/<id>')
def getComentarioById(id):
    # EJ: persona/getById/2
    # Filtra por id
    #usuario=db.session.query(Usuario).get(usuarioId)
    comentario =  db.session.query(Comentario).get(id)
    #return render_template('comentario.html',comentario=comentario)



#NO se usa
@app.route('/usuario/list')
def listarUsuarios():
    # EJ: persona/list
    usuarios = db.session.query(Usuario).all()
    return render_template('usuarios.html',usuarios=usuarios,filtro="")

#Función que permite al user registrarse en la BD
@app.route('/usuario/crear/<nombre>/<apellido>/<email>/<password>')
def crearUsuario(nombre,apellido,email,password,admin=False):
    #Crear una persona
    usuario = Usuario(nombre=nombre, apellido=apellido,email=email,passworden=password,admin=admin)
    #Agregar a db
    db.session.add(usuario)
    #Hacer commit de los cambios
    db.session.commit()
    #Envía la persona a la vista
    #return render_template('usuario.html',usuario=usuario)

#No se usa
@app.route('/usuario/getById/<id>')
def getUsuarioById(id):
    # EJ: persona/getById/2
    # Filtra por id
    usuario =  db.session.query(Usuario).get(id)
    #Envía la persona a la vista
    return render_template('usuario.html',usuario=usuario)

#NO se usa
@app.route('/usuario/eliminar/<id>')
def eliminarUsuario(id):
    # EJ: persona/eliminar/1
    #Obtener persona por id
    usuario = db.session.query(Usuario).get(id)
    #Eliminar de la db
    db.session.delete(usuario)
    #Hacer commit de los cambios
    db.session.commit()
    return redirect(url_for('listarUsuarios'))
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
