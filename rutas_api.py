from flask import redirect, url_for, request
from datetime import datetime
from app import app,db,csrf
from modelos import *
from flask import jsonify #se convierten a json
from funciones_mail import enviarMail
from sqlalchemy.exc import SQLAlchemyError
from errores import escribir_log


#Listar Eventos
#curl -H "Accept:application/json" http://localhost:5000/api/evento
@app.route('/api/evento', methods=['GET'])
def apiListarEventos():
    eventos = db.session.query(Evento).filter(Evento.aprobado==0).all()
    #Recorrer la lista de eventos convirtiendo cada una a JSON
    return jsonify({ 'eventos': [evento.a_json() for evento in eventos] })


#Traer evento por id
#curl -H "Accept:application/json" http://localhost:5000/admin/api/evento/15
@app.route('/admin/api/evento/<id>', methods=['GET'])
def apiGetEventoById(id):
    evento =  db.session.query(Evento).get_or_404(id)
    #Convertir el evento creada en JSON
    return jsonify(evento.a_json())



#Actualizar Evento
#curl -i -X PUT -H "Content-Type:application/json" -H "Accept:application/json" http://localhost:5000/admin/api/evento/12 -d '{"nombre":"Maria"}'
@app.route('/admin/api/evento/<id>', methods=['PUT'])
@csrf.exempt #para deshabilitar la protección CSRF para una vista en particular
def apiActualizarEvento(id):
    evento =  db.session.query(Evento).get_or_404(id)
      #El request.json.get lo que hace primero es buscar la clave que le indiquemos como primer parametro en el JSON del curl, si la encuentra ,
    # obtenemos su valor y lo igualamos al atributo del evento correspondiente, en caso contrario utiliza el segundo parametro que es el valor
    # por defecto que ya estaba seteado anteriormente.
    evento.nombre = request.json.get('nombre', evento.nombre)
    evento.fecha = request.json.get('fecha', evento.fecha)
    evento.tipo = request.json.get('tipo', evento.tipo)
    evento.descripcion = request.json.get('descripcion', evento.descripcion)
    evento.aprobado = request.json.get('aprobado',evento.aprobado)
    evento.aprobado=False
    db.session.add(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en apiActualizarEvento en rutas_api.py")
    #Convertir la persona actualizada en JSON
    #Pasar código de status
    return jsonify(evento.a_json()) , 201 #codigo que se envia de regreso #Convertimos el evento actualizado a JSON y indicamos con el status 201
                                         # que la operacion modifico el recurso (evento) con exito


#Eliminar Evento
#curl -i -X DELETE -H "Accept: application/json" http://localhost:5000/admin/api/evento/12
@app.route('/admin/api/evento/<id>', methods=['DELETE'])
@csrf.exempt
def apiEliminarEvento(id):
    evento = db.session.query(Evento).get_or_404(id)
    db.session.delete(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en apiEliminarEvento en rutas_api.py")
    #Pasar código de status
    return '', 204 #Retornamos el status 204, que indica que no hay contenido por retornar.


#Aprobar Evento
#curl -X POST -i -H  "Content-Type:application/json" -H "Accept:application/json" http://127.0.0.1:5000/admin/evento/aprobar/id
@app.route('/admin/evento/aprobar/<id>',methods=['POST'])
@csrf.exempt
def aprobarEventosApi(id):
    evento=db.session.query(Evento).get(id)
    evento.aprobado=True
    email=evento.usuario.email
    enviarMail(email, 'Evento Aprobado por el Admin', 'evento_aprobado')
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en aprobarEventosApi en rutas_api.py")
    print("El evento ha sido aprobado")
    return jsonify({'Evento':[evento.a_json()]})

#________________________________________---Para comentarios--------_______________________-

#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:5000/admin/api/comentarios/17
@app.route('/admin/api/comentarios/<id>', methods=['GET'])
def apiListarComentarios(id):
    comentario = db.session.query(Comentario).get(id)
    return jsonify(comentario.a_json())

#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:5000/api/evento/comentarios/24
@app.route('/api/evento/comentarios/<id>',methods=['GET'])
def apiGetComentarioById(id):
    comentarios= db.session.query(Comentario).filter(Comentario.eventoId==Evento.eventoId,Comentario.eventoId==id,Evento.eventoId==id)
    return jsonify({ 'Comentarios': [comentario.a_json() for comentario in comentarios] })

#curl -i -X DELETE -H "Accept: application/json" http://localhost:5000/api/deletecomentario/60
@app.route('/api/deletecomentario/<id>',methods=['DELETE'])
@csrf.exempt
def eliminarComentarioApi(id):
    comentario =db.session.query(Comentario).get(id)
    db.session.delete(comentario)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        escribir_log(str(e._message()), "Error en base de datos en eliminarComentarioApi en rutas_api.py")
    print("Comentario borrado Exitosamente")
    return '',204
