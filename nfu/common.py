from functools import wraps
from hashlib import md5
from os import getenv
from random import choice
from string import ascii_letters, digits
from time import time

from flask import g, jsonify, request
from redis import Redis

from nfu.expand.token import validate_token
from nfu.models import BusUser, User
from nfu.nfu_error import NFUError


def generate_expires_timestamp(expires_in: int = 600) -> int:
    """
    生成过期时间戳
    :param expires_in:
    :return:
    """
    return int(time() + expires_in)


def generate_password(length: int = 32, chars: str = ascii_letters + digits) -> str:
    """
    生成随机密码
    :param length:
    :param chars:
    :return:
    """
    return ''.join([choice(chars) for i in range(length)])


def generate_cdn_key(uri: str, timestamp: int, rand: str) -> str:
    """
    生成cdn鉴权key
    :param uri:
    :param timestamp:
    :param rand:
    :return:
    """
    return md5(f"{uri}-{timestamp}-{rand}-0-{getenv('CDN_PRIVATE_KEY')}".encode(encoding="UTF-8")).hexdigest()


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
        raise NFUError('没有访问权限', code='1001')

    if token == 'null' or token_type.lower() != 'bearer':
        raise NFUError('没有访问权限', code='1001')

    return token


def get_config(func):
    """
    获取当前学年学期等基本配置

    :param func: 使用此装饰器的函数
    :return: 指向新函数，或者返回错误
    """

    @wraps(func)
    def wrapper(*args, **kw):
        school_year = 2019
        semester = 1

        return func(school_year, semester, *args, **kw)

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

        g.user = User.query.get(validate['id'])

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
