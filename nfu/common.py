from functools import wraps
from os import getenv

from flask import g, jsonify, request
from redis import Redis

from nfu.expand.token import validate_token
from nfu.models import User
from nfu.NFUError import NFUError


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

        if g.user.bus_session is None:
            return jsonify({'message': '没有访问权限'})

        else:
            return func(*args, **kw)

    return wrapper


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
