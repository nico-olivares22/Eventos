from flask import Flask
from flask_sqlalchemy import SQLAlchemy #Incluye sqlAlchemy
from sqlalchemy import or_
from flask_wtf import CSRFProtect #importar para proteccion CSRF
from dotenv import load_dotenv #carga variables de entorno
import os
from flask_mail import Mail, Message  # Importar para enviar Mail
from flask_login import LoginManager


app = Flask(__name__)
load_dotenv()

#Sicronización con la BD
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True #Sigue las modificaciones en tiempo real
#Configuración de conexion de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+os.getenv('DB_USERNAME')+':'+os.getenv('DB_PASS')+'@localhost/consultas'
#Instancia que representa la base de datos
db = SQLAlchemy(app)
csrf = CSRFProtect(app) #Iniciar protección CSRF


#Configuración mail
# Configuraciones de mail
app.config['MAIL_HOSTNAME'] = 'localhost'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SENDER'] = 'Master Eventos <Mastereventos@eventos.com>'


mail = Mail(app)  # Inicializar mail
login_manager = LoginManager(app)
#csrf = CSRFProtect(app)
app.secret_key = os.getenv('SECRET_KEY')



if __name__ == '__main__': #Asegura que solo se ejectue el servidor cuando se ejecute el script directamente
    from rutas import *
    from rutas_api import *
    from errores import *
    app.run(debug=True)
