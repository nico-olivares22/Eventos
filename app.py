from flask import Flask
from flask_sqlalchemy import SQLAlchemy #Incluye sqlAlchemy
from sqlalchemy import or_
from dotenv import load_dotenv #carga variables de entorno
import os

app = Flask(__name__)
load_dotenv()

#Sicronización con la BD
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True #Sigue las modificaciones en tiempo real
#Configuración de conexion de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+os.getenv('DB_USERNAME')+':'+os.getenv('DB_PASS')+'@localhost/consultas'
#Instancia que representa la base de datos
db = SQLAlchemy(app)

#Ejecutar pip install -r requirements.txt


if __name__ == '__main__': #Asegura que solo se ejectue el servidor cuando se ejecute el script directamente
    from rutas import *
    app.run(port = 7000, debug = True)
