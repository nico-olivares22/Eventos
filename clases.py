# - *- coding: utf- 8 - *-
from flask_wtf import FlaskForm #Importa funciones de formulario
from wtforms import StringField, TextField , HiddenField, PasswordField, TextAreaField, SelectField, SubmitField, RadioField #Importa campos
from wtforms.fields.html5 import EmailField,DateField #Importa campos HTML
from wtforms import validators #Importa validaciones
from wtforms_components import TimeField
from flask_wtf.file import FileField, FileRequired, FileAllowed #Importa funciones, validaciones y campos de archivo


#Clase de Registro
class Registro(FlaskForm):


    #Lista de opciones usada para select
    #lista_opciones = [
        #('1','Opción 1'),
        #('2','Opción 2'),
        #('3','Opción 3'),
        #('4','Opción 4')
    #]
    #Lista de opciones usada para radio button
    lista_sexo = [
        ('f','Femenino'),
        ('m','Masculino'),
    ]

    #Definición de campo String
    nombre = StringField('Nombre',
    [
        #Definición de validaciones
        validators.Required(message = "Completar nombre")
    ])

    apellido = StringField('Apellido',
    [
        validators.Required(message = "Completar apellido")
    ])



    #Definición de campo de contraseña
    password = PasswordField('Contraseña', [
        validators.Required(),
         #El campo de contraseña debe coincidir con el de confirmuar
        validators.EqualTo('confirmar', message='La contraseña no coincide')
    ])

    confirmar = PasswordField('Repetir contraseña')

    #Definición de campo de correo
    email = EmailField('Correo',
    [
        validators.Required(message = "Completar email"),
        validators.Email( message ='Formato de mail incorrecto')
    ])



    #bio = TextAreaField('Biografía')

    #Definición de campo select
    #opciones = SelectField('Opción', choices=lista_opciones)

    #Definición de campo submit
    submit1 = SubmitField("Registrarse")

class CrearEvento(FlaskForm):

    #Función para hacer campo opcional
    def opcional(field):
        field.validators.insert(0, validators.Optional())

    titulo= StringField('Titulo',
    [
        #Definición de validaciones
        validators.Required(message = "Completar Titulo de Evento")
    ])

    fechaEven = DateField('Fecha del Evento',
    [
        validators.DataRequired(message = "Completar Fecha del Evento")
    ])

    hora = TimeField('Hora del Evento',
    [
        #Definición de validaciones
        validators.Required(message = "Completar con la Hora del Evento")
    ])

    tipo = [
        ('1','--Ingrese tipo de evento--'),
        ('Fiesta','Fiesta'),
        ('Conferencia','Conferencia'),
        ('Festival','Festival'),
        ('Obra','Obra')
    ]
    opciones = SelectField('Opción', choices=tipo)
    #Definición de campo de archivo
    imagen = FileField(validators=[
        FileRequired(),
        #Validación de tipo de archivo
        FileAllowed(['jpg', 'png'], 'El archivo debe ser una imagen jpg o png')
    ])

    descripcion = StringField('Breve Descripcion',
    [
        #Definición de validaciones
        validators.Required(message = "Breve Descripcion")
    ])

    #Definición de campo submit
    submit = SubmitField("CrearEvento")
class Comentarios(FlaskForm):
    campocomentario= StringField('Comentario',
    [
        #Definición de validaciones
        validators.Required(message = "Comentario")
    ])
    fechahora = DateField('Fecha y Hora del Comentario',
    [
        validators.DataRequired(message = "Completar Fecha y Hora del Comentario")
    ])
    submit = SubmitField("Enviar")

class Inicio(FlaskForm):

    email = EmailField('Correo',
    [
        validators.Required(message = "Completar email"),
        validators.Email( message ='Formato de mail incorrecto')
    ])


    password = PasswordField('Contraseña', [
        validators.Required(),
    ])
    submit_ingreso = SubmitField("Iniciar Sesión")
class Filtro(FlaskForm):


    fecha_desde = DateField('Desde que fecha quiere buscar',
    [
        validators.DataRequired(message="Ingrese una fecha válida")
    ])
    fecha_hasta = DateField('Hasta que fecha quiere buscar',
    [
        validators.DataRequired(message="Ingrese una fecha válida")
    ])
    tipo_evento = [
        ('1','--Ingrese tipo de evento--'),
        ('Fiesta','Fiesta'),
        ('Conferencia','Conferencia'),
        ('Festival','Festival'),
        ('Obra','Obra'),
        ('Otro','Otro')
    ]

    opciones = SelectField('Opción', choices=tipo_evento)

    #Definición de campo submit
    submit = SubmitField("Filtrar")
