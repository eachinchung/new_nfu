from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer


def generate_token(user):
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=3600)
    token = s.dumps({'id': user.id}).decode('ascii')
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=1296000)
    remember_token = s.dumps({'id': user.id}).decode('ascii')
    return token, remember_token
