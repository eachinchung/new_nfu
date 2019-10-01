from functools import wraps

from flask import request, jsonify

from nfu.models import User
from nfu.token import validate_token


def check_access_token(func):
    """
    检查用户的access_token是否合法
    因为有账号才能拿到token，故不考虑，账号不存在的情况

    :param func: 使用此装饰器的函数
    :return: 指向新函数，或者返回错误
    """

    @wraps(func)
    def wrapper(*args, **kw):
        token = request.values.get('access_token')
        if token is None:
            return jsonify({'message': '没有访问权限'}), 403

        validate = validate_token(token)
        # 验证 token 是否通过
        if not validate[0]:
            return jsonify({'message': validate[1]}), 403

        user = User.query.get(validate[1]['id'])
        return func(user, *args, **kw)

    return wrapper
