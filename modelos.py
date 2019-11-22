from flask import url_for
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash #Permite generar y verificar pass con hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #Genera los token de confirmación para ccomparar token de logeo
from flask_login import UserMixin, LoginManager #cuestiones de login en la app
class Evento(db.Model): #El objeto heredan el modelo para poder trabajar con los tablas
    eventoId = db.Column(db.Integer, primary_key=True) #clave primaria
    nombre = db.Column(db.String(90), nullable=False) #no puede ser nulo
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    descripcion = db.Column(db.String(500), nullable= True)
    imagen = db.Column(db.String(40), nullable=False)
    tipo = db.Column(db.String(15), nullable=False)
    aprobado = db.Column(db.Boolean, nullable=False, default=False)
    #Relación entre evento y usuario
    usuarioId=db.Column(db.Integer, db.ForeignKey('usuario.usuarioId'), nullable=False) #clave foranea para relacionar 1 objeto con muchos objetos, en este caso un usuario puede tener muchos eventos
    usuario=db.relationship("Usuario", back_populates="eventos") #con el back_populates el usuario puede tener muchos eventos
    #Relación entre evento y comentario
    comentarios=db.relationship("Comentario", back_populates="evento", cascade="all,delete-orphan") #con el delete-orphan si borro un evento se borraran todos los comentarios

    def __repr__(self):
        return '<Evento: %r %r %r %r %r %r %r>' % (self.eventoId,self.nombre, self.fecha,self.hora, self.descripcion, self.imagen, self.tipo)

    #Convertir objeto en JSON
    def a_json(self):
        evento_json = {
            'eventoId': url_for('apiGetEventoById', id=self.eventoId, _external=True), #ruta para acceder al evento
            'nombre': self.nombre,
            'fecha': self.fecha,
            'tipo': self.tipo,
        }
        return evento_json
    @staticmethod #El self es como funciones planas excepto que las puede llamar desde la clase o desde una instancia de la clase:
    #Convertir JSON a objeto
    def desde_json(evento_json): #clave valor
        nombre = evento_json.get('nombre')
        fecha = evento_json.get('fecha')
        tipo = evento_json.get('tipo')
        return Evento(nombre=nombre, fecha=fecha, tipo=tipo)

class Usuario(UserMixin,db.Model):
    usuarioId = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    apellido = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(130), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    #Relación entre evento y usuario
    eventos=db.relationship("Evento", back_populates="usuario", cascade="all, delete-orphan")
    #Relación entre usuario y comentario
    comentarios=db.relationship("Comentario", back_populates="usuario", cascade="all, delete-orphan")
    #No permitir leer la pass de un usuario
    @property #que no se pueda leer la contraseña asi nomas
    def passworden(self):
        raise AttributeError('La password no puede leerse')
    #Al setear la pass generar un hash
    @passworden.setter
    def passworden(self, passworden):
        self.password = generate_password_hash(passworden) #encriptar contraseña
    def get_id(self):
           return (self.usuarioId)
    #Al verififcar pass comparar hash del valor ingresado con el de la db
    def verificar_pass(self, passworden):
        return check_password_hash(self.password, passworden)
    def is_admin(self):
        auxiliar=False
        if self.admin==1:
            auxiliar=True
        return auxiliar
    def __repr__(self):
        return '<Usuario: %r %r %r %r %r %r >' % (self.usuarioId,self.nombre,self.apellido, self.email, self.password,self.admin)
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Comentario(db.Model):
    comentarioId = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(500), nullable = False)
    fechahora = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    #Relación entre usuario y comentario
    usuarioId=db.Column(db.Integer,db.ForeignKey('usuario.usuarioId'),nullable=False)
    usuario=db.relationship("Usuario", back_populates="comentarios")
    #Relación entre evento y comentario
    eventoId=db.Column(db.Integer, db.ForeignKey('evento.eventoId'), nullable=False)
    evento= db.relationship("Evento", back_populates="comentarios")
    def __repr__(self):
        return '<Comentario: %r %r %r >' % (self.comentarioId,self.contenido, self.fechahora)

    #Convertir objeto en JSON
    def a_json(self):
        comentario_json = {
            'comentarioId': url_for('apiGetComentarioById', id=self.comentarioId, _external=True), #ruta para acceder a persona
            'contenido': self.contenido,
            'fechahora': self.fechahora,
        }
        return comentario_json
