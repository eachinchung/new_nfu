from os import getenv

from flask_mail import Message
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature, SignatureExpired

from nfu.extensions import mail


# 生成令牌
def generate_token(data: dict, *, token_type: str = 'ACCESS_TOKEN', expires_in: int = 3600) -> tuple:
    s = TimedJSONWebSignatureSerializer(getenv(token_type), expires_in=expires_in)
    token = s.dumps(data).decode('ascii')
    return token


# 验证令牌
def validate_token(token: str, token_type: str = 'ACCESS_TOKEN') -> tuple:
    s = TimedJSONWebSignatureSerializer(getenv(token_type))
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return False, '签名错误，或证书已过期'
    else:
        return True, data


# 发送邮件
def send_email(subject, to, body, html=None):
    message = Message(subject, recipients=to)
    message.body = body
    if html is not None:
        message.html = html
    mail.send(message)
