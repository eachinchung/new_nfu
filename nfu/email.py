from threading import Thread

from flask import current_app
from flask_mail import Message

from nfu.extensions import mail


# 发送邮件，供多线程调用
def send_async_mail(my_app, message: Message) -> None:
    with my_app.app_context():
        mail.send(message)


# 发送邮件
def send_email(subject: str, to: str, body: str, html=None) -> None:
    # noinspection PyProtectedMember
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to])
    message.body = body
    if html is not None:
        message.html = html

    Thread(target=send_async_mail, args=[app, message]).start()
