from os import getenv

from itsdangerous import BadSignature, SignatureExpired, TimedJSONWebSignatureSerializer

from nfu.models import BusUser, Dormitory
from nfu.nfu_error import NFUError


def create_access_token(user) -> dict:
    """
    生成访问令牌
    """
    # dormitory = Dormitory.query.get(user.room_id)
    token_data = {
        'id': user.id,
        # 'name': user.name,
        # 'email': user.email,
        # 'dormitory': f'{dormitory.building} {dormitory.floor} {dormitory.room}',
        'busPower': BusUser.query.get(user.id) is not None
    }

    return {
        'code': '1000',
        'message': {
            'accessToken': generate_token(token_data),
            'refreshToken': generate_token({'id': user.id}, token_type='REFRESH_TOKEN', expires_in=2592000)
        }
    }


def generate_token(data: dict, *, token_type: str = 'ACCESS_TOKEN', expires_in: int = 3600) -> str:
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


def validate_token(token: str, token_type: str = 'ACCESS_TOKEN') -> dict:
    """
    验证令牌
    :param token: 令牌
    :param token_type: 令牌类型
    """
    s = TimedJSONWebSignatureSerializer(getenv(token_type))
    try:
        data = s.loads(token)
    except SignatureExpired:
        raise NFUError('签名已过期', code='1001')
    except BadSignature:
        raise NFUError('签名错误', code='1002')
    else:
        return data
