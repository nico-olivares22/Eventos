from flask import render_template,request, jsonify
from app import app
import datetime
from datetime import date
from formularios import Inicio

#Manejar error de página no encontrada
@app.errorhandler(404)
def page_not_found(e):
    formulario_ingreso=Inicio()
    #Si la solicitud acepta json y no HTML
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        #Responder con JSON
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    #Sino responder con template HTML
    return render_template('404.html',formulario_ingreso=formulario_ingreso), 404

#Manejar error de error interno
@app.errorhandler(500)
def internal_server_error(e):
    escribir_log("Error 500 Problema Interno", "Unknown")
    #Si la solicitud acepta json y no HTML
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        #Responder con JSON
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    #Sino responder con template HTML
    return render_template('500.html'), 500

#Manejar error de metodo no permitido
@app.errorhandler(405)
def metodo_no_permitido(e):
    formulario_ingreso=Inicio()
    #Si la solicitud acepta json y no HTML
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        #Responder con JSON
        response = jsonify({'error': 'internal server error'})
        response.status_code = 405
        return response
    #Sino responder con template HTML
    return render_template('405.html',formulario_ingreso=formulario_ingreso), 405



def escribir_log(error,acontecimiento):
    archivo = open('error.log','a')
    archivo.write(f"\n{datetime.datetime.now()}, {error}, Funcion: {acontecimiento}\n")
    archivo.close()
    #print(archivo)
