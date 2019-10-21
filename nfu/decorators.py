from functools import wraps

from flask import g, jsonify, request

from nfu.models import User
from nfu.expand.token import validate_token


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
        token = request.values.get('access_token')

        if token is None:
            return jsonify({'message': '没有访问权限'}), 403

        # 验证 token 是否通过
        validate = validate_token(token)
        if not validate[0]:
            return jsonify({'message': validate[1]}), 403

        g.user = User.query.get(validate[1]['id'])
        g.user_power = validate[1]

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
        if not g.user_power['school_bus']:
            return jsonify({'message': '没有访问权限'}), 403

        return func(*args, **kw)

    return wrapper
