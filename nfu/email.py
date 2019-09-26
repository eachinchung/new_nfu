from os import getenv
from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from nfu.extensions import mail


# 发送邮件，供多线程调用
def __send_async_mail(my_app, message: Message) -> None:
    # my_app 的意义是激活 flask 上下文
    with my_app.app_context():
        mail.send(message)


# 发送邮件
def send_email(subject: str, to: str, body: str, html: str = None) -> None:
    # noinspection PyProtectedMember
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to])
    message.body = body
    # 为增加代码的复用性，我们支持发送纯文本邮件
    if html is not None:
        message.html = html

    # 异步发送
    Thread(target=__send_async_mail, args=[app, message]).start()


# 发送验证邮箱的邮件
def send_validate_email(to: str, name: str, user_id: int, token) -> None:
    # url 拼接实例 http://127.0.0.1:5000/validate/email/token
    url = getenv('API_URL') + '/validate/email/' + token
    body = render_template('email/validate_email.txt', name=name, user_id=user_id, url=url)
    send_email('请验证您的邮箱地址', to, body)
