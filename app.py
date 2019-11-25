from flask import Flask
from flask_sqlalchemy import SQLAlchemy #Incluye sqlAlchemy
from flask_wtf import CSRFProtect #importar para proteccion CSRF
from dotenv import load_dotenv #carga variables de entorno
import os #para cargar variables de entorno
from flask_mail import Mail  # Importar para enviar Mail
from flask_login import LoginManager #para manejar login de usuarios


app = Flask(__name__) #se crea la app Flask
load_dotenv() #permite acceder a las variables de entorno

#Sicronización con la BD
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True #Sigue las modificaciones en tiempo real
#Configuración de conexion de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+os.getenv('DB_USERNAME')+':'+os.getenv('DB_PASS')+'@localhost/consultas'
#Instancia que representa la base de datos
db = SQLAlchemy(app) #Instancia que representa la BD
csrf = CSRFProtect(app) #Iniciar protección CSRF,  es un método por el cual un usuario malintencionado intenta hacer que tus usuarios, sin saberlo, envíen datos que no quieren enviar.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') #clave secreta


#Configuraciones de Mail
#iP del host de salida
app.config['MAIL_HOSTNAME'] = 'localhost'
#Servidor de mail usado
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
#Puerto del mail saliente
app.config['MAIL_PORT'] = 587
#Especificar conexión con SSL/TLS
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SENDER'] = 'Master Eventos <Mastereventos@eventos.com>'


mail = Mail(app)  #Inicializar objeto de aplicacion Mail
login_manager = LoginManager(app) #Inicializar objeto de aplicacion LoginManager
app.secret_key = os.getenv('SECRET_KEY') #Accedere a la clave secreta



if __name__ == '__main__': #Asegura que solo se ejectue el servidor cuando se ejecute el script directamente
    from rutas import *
    from rutas_api import *
    from errores import *
    app.run(debug=False)
