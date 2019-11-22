from app import mail, app,db
from flask_mail import Mail, Message
from flask import render_template
from threading import Thread
from modelos import *
from errores import escribir_log
import smtplib,os

def enviarMail(to, subject, template, **kwargs):
    #Configurar asunto, emisor y destinatarios
    mensaje = Message(subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    mensaje.body = render_template('mail/' + template + '.txt', **kwargs) #accede al txt de la carpeta mail donde está el texto que va al html
    mensaje.html = render_template('mail/' + template + '.html', **kwargs) #accede al html de envio que le llega al user
    thr = Thread(target=mail_enviado, args=[app, mensaje])
    # Iniciar hilo para mandar mail rápido
    thr.start()

def mail_enviado(app, mensaje):

    with app.app_context():
        try:
            mail.send(mensaje)
        #Generar código de error dependiendo de la excepción
        except smtplib.SMTPSenderRefused as e:
            sms = str(e)
            escribir_log(sms,"Error en funciones_mail")
        except smtplib.SMTPAuthenticationError as e:
            sms = str(e)
            escribir_log(sms,"Error en funciones_mail")
        except smtplib.SMTPServerDisconnected as e:
            sms = str(e)
            escribir_log(sms,"Error en funciones_mail")
        except smtplib.SMTPException as e:
            error = str(e)
            escribir_log(error,"Error en funciones_mail")
        except OSError as e:
            error = str(e)
            escribir_log(error,"Error en funciones_mail")


#funcion para validar email existente
def validar_mailExistente(email):
    auxiliar = False

    if db.session.query(Usuario).filter(Usuario.email.ilike(email)).count() == 0:
        auxiliar = True
    return auxiliar
