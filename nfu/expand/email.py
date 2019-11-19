from os import getenv
from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from nfu.extensions import mail


def __send_async_mail(my_app, message: Message) -> None:
    """
    私有函数，发送邮件，供多线程调用
    :param my_app: 激活 flask 上下文
    :param message: 邮件的内容
    :return:
    """
    with my_app.app_context():
        mail.send(message)


def send_email(subject: str, to: str, body: str, html: str = None) -> None:
    """
    发送邮件
    :param subject: 邮件标题
    :param to: 收件人
    :param body: 文本类型邮件内容
    :param html: html类型邮件内容（可选）
    :return:
    """
    # noinspection PyProtectedMember
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to])
    message.body = body

    # 为增加代码的复用性，我们支持发送纯文本邮件
    if html is not None:
        message.html = html

    # 异步发送
    Thread(target=__send_async_mail, args=[app, message]).start()


def send_validate_email(to: str, name: str, user_id: int, token) -> None:
    """
    发送验证邮箱的邮件

    url 拼接实例 http://127.0.0.1:5000/validate/email/token

    :param to: 收件人
    :param name: 用户姓名
    :param user_id: 学号
    :param token: 激活邮箱的token
    :return:
    """
    url = getenv('FRONT_END_URL') + '/activation?token=' + token
    body = render_template('email/validate_email.txt', name=name, user_id=user_id, url=url)
    html = render_template('email/validate_email.html', name=name, user_id=user_id, url=url)
    send_email('请验证您的邮箱地址', to, body, html)


def send_verification_code(to: str, name: str, code: int) -> None:
    """
    发送验证码

    url 拼接实例 http://127.0.0.1:5000/validate/email/token

    :param to: 收件人
    :param name: 用户姓名
    :param code: 验证码
    :return:
    """
    body = render_template('email/verification_code.txt', name=name, code=code)
    html = render_template('email/verification_code.html', name=name, code=code)
    send_email('您的验证码', to, body, html)
