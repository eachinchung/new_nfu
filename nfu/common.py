import base64
from functools import wraps
from json import loads
from os import getenv

from flask import g, jsonify, request
from redis import Redis

from nfu.expand.token import validate_token
from nfu.models import BusUser, User
from nfu.nfu_error import NFUError


def safe_base64_decode(s: str) -> str:
    """
    url 安全的 base64 解码
    :param s:
    :return:
    """
    # 判断是否是4的整数u，不够的在末尾添加等号
    if len(s) % 4 != 0:
        s = s + '=' * (4 - len(s) % 4)

    # 解决字符串和bytes类型
    if not isinstance(s, bytes):
        s = bytes(s, encoding='utf-8')

    # 解码
    base64_str = base64.urlsafe_b64decode(s)

    return base64_str


def verification_code(code: int) -> None:
    """
    验证验证码
    :return:
    """

    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)

    try:
        if int(r.get(g.user.id)) == code:

            # 删除缓存中的数据
            r.delete(g.user.id)

        else:
            raise NFUError('验证码错误', code='2001')

    except TypeError:
        raise NFUError('验证码错误', code='2001')


def get_token() -> str:
    """
    从请求头获取token
    :return:
    """

    try:
        token_type, token = request.headers['Authorization'].split(None, 1)
    except (KeyError, ValueError):
        raise NFUError('请重新登录', code='1001')

    if token == 'null' or token_type.lower() != 'bearer':
        raise NFUError('请重新登录', code='1001')

    return token


def get_school_config(func):
    """
    获取当前学年学期等基本配置

    :param func: 使用此装饰器的函数
    :return: 指向新函数，或者返回错误
    """

    @wraps(func)
    def wrapper(*args, **kw):
        g.school_config = {
            'schoolYear': 2020,
            'semester': 1,
            'schoolOpensTimestamp': 1600012800000
        }

        return func(*args, **kw)

    return wrapper


def check_access_token(func):
    """
    检查用户的access_token是否合法
    因为有账号才能拿到token，故不考虑，账号不存在的情况

    使用flask的g对象，全局储存，user、user_power数据

    :param func: 使用此装饰器的函数
    :return: 指向新函数，或者返回错误
    """

    @wraps(func)
    def wrapper(*args, **kw):

        # 验证 token 是否通过
        try:
            validate = validate_token(get_token())
        except NFUError as err:
            return jsonify({'code': err.code, 'message': err.message})

        r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)
        user_data = loads(validate['data'])
        g.user = User(
            id=validate['id'],
            name=user_data["name"],
            room_id=user_data["roomId"],
            email=user_data["email"],
            jw_pwd=r.get(f"jw-{validate['id']}").decode('utf-8')
        )

        return func(*args, **kw)

    return wrapper


def check_power_school_bus(func):
    """
    检查用户否具有校车功能的权限

    :param func: 使用此装饰器的函数
    :return: 指向新函数，或者返回错误
    """

    @wraps(func)
    def wrapper(*args, **kw):
        g.refresh = True
        g.bus_user = BusUser.query.get(g.user.id)

        if g.bus_user is None:
            return jsonify({'message': '没有访问权限'})

        else:
            return func(*args, **kw)

    return wrapper
