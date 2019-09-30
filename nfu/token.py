from os import getenv
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature, SignatureExpired


def generate_token(data: dict, *, token_type: str = 'ACCESS_TOKEN', expires_in: int = 3600) -> tuple:
    """
    生成令牌
    :param data: 令牌的内容
    :param token_type: 令牌的类型，每一个类型对应不同的密钥
    :param expires_in: 有效时间
    :return: 令牌
    """
    s = TimedJSONWebSignatureSerializer(getenv(token_type), expires_in=expires_in)
    token = s.dumps(data).decode('ascii')
    return token


def validate_token(token: str, token_type: str = 'ACCESS_TOKEN') -> tuple:
    """
    验证令牌
    :param token: 令牌
    :param token_type: 令牌类型
    :return: 一个元组，通常我规定第一个为bool，用来判定是否成功获取数据。
    """
    s = TimedJSONWebSignatureSerializer(getenv(token_type))
    try:
        data = s.loads(token)
    except SignatureExpired:
        return False, '签名已过期'
    except BadSignature:
        return False, '签名错误'
    else:
        return True, data
