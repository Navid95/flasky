from . import mail
from flasky import app
from flask_mail import Message
from threading import Thread


def send_async_mail(msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, body):
    msg = Message()
    msg.body = body
    msg.subject = subject
    msg.recipients = [to]
    msg.sender = 'Flasky Admin <navid.me@mtnirancell.ir>'
    thr = Thread(target=send_async_mail, args=[msg])
    thr.start()
    return thr

