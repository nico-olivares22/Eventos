from app import mail, app,db
from flask_mail import Mail, Message
from flask import render_template
from threading import Thread
from modelos import *


def enviarMail(to, subject, template, **kwargs):
    mensaje = Message(subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    mensaje.body = render_template('mail/' + template + '.txt', **kwargs)
    mensaje.html = render_template('mail/' + template + '.html', **kwargs)
    thr = Thread(target=mail_enviado, args=[app, mensaje])
    # Iniciar hilo
    thr.start()

def mail_enviado(app, mensaje):

    with app.app_context():
        print(mensaje.subject)
        print(mensaje.sender)
        print(str(mensaje.recipients))
        mail.send(mensaje)


#funcion para validar email existente
def validar_mailExistente(email):
    auxiliar = False

    if db.session.query(Usuario).filter(Usuario.email.ilike(email)).count() == 0:
        auxiliar = True
    return auxiliar
