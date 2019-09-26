from os import getenv
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature, SignatureExpired


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
    except BadSignature:
        return False, '签名错误'
    except SignatureExpired:
        return False, '签名已过期'
    else:
        return True, data
