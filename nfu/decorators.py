from functools import wraps

from flask import request

from nfu.models import User
from nfu.token import validate_token


def check_login(func):
    """
    检查用户的access_token是否合法
    因为有账号才能拿到token，故不考虑，token不存在的情况

    :param func: 使用此装饰器的函数
    :return: 指向新函数
    """

    @wraps(func)
    def wrapper(*args, **kw):
        token = request.form.get('access_token')
        validate = validate_token(token)

        # 验证 token 是否通过
        if validate[0]:
            user = User.query.get(validate[1]['id'])
            error = None

        else:
            user = None
            error = validate[1]

        return func(user, error, *args, **kw)

    return wrapper
