from . import mail
from flasky import app
from flask_mail import Message
from threading import Thread
from flask import render_template


def send_async_mail(msg):
    with app.app_context():
        mail.send(msg)


def send_mail_v2(to, subject, template, **kwargs):
    """
    General send email function, it is advised to develop atomic functions on top of this function for regularly used emails in the application, but for sure the function can be used directly.

    :param to: list of recipients email addresses(str)
    :param subject: the subject of the email to be sent, 'FLASKY_MAIL_SUBJECT_PREFIX' environment variable will be concatenated to the start of the subject
    :param template: the template from which the email body/html is created (both .txt & .html files will be rendered).
    :param kwargs: keyword args needed by the template
    :return: a new Thread obj corresponding to the mail that was sent
    """
    mail_subject = app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject
    recipients = list(to)
    # body = render_template(template + '.txt', **kwargs)
    html = render_template(template + '.html', **kwargs)
    sender = app.config['FLASKY_MAIL_SENDER']
    msg = Message(subject=mail_subject, recipients=recipients, html=html, sender=sender)
    # msg = Message(subject=mail_subject, recipients=recipients, body=body, html=html, sender=sender)
    thr = Thread(target=send_async_mail, args=[msg])
    thr.start()
    return thr


def send_mail(to, subject, **kwargs):
    msg = Message()
    msg.body = kwargs.get('body')
    msg.subject = subject
    msg.recipients = [to]
    msg.sender = 'Flasky Admin <navid.me@mtnirancell.ir>'
    thr = Thread(target=send_async_mail, args=[msg])
    thr.start()
    return thr


def send_registration_confirm_link(user):
    to = list()
    to.append(user.email)
    subject = f'Please confirm your account'
    template = f'auth/email/confirmation_email'
    send_mail_v2(to=to, subject=subject, template=template, user=user,
                 token=user.generate_user_token())


def send_password_reset_link(user):
    print(f'{__name__}: user email address is {user.email}')
    to = list()
    to.append(user.email)
    subject = f'Password reset link'
    template = f'auth/email/reset_password'
    send_mail_v2(to=to, subject=subject, template=template, user=user,
                 token=user.generate_user_token())


def send_email_update_link(user, new_email):
    print(f'{__name__}: user\'s new email address is {new_email}')
    to = list()
    to.append(new_email)
    subject = f'Email Update Link'
    template = f'auth/email/email_update'
    send_mail_v2(to=to, subject=subject, template=template, user=user,
                 token=user.generate_email_update_token(new_email))


