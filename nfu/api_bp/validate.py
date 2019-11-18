from os import getenv

from flask import Blueprint, jsonify
from redis import Redis

from nfu.common import get_token
from nfu.expand.token import validate_token
from nfu.extensions import db
from nfu.NFUError import NFUError
from nfu.models import User

validate_bp = Blueprint('validate', __name__)


@validate_bp.route('/email')
def activation():
    """
    验证邮箱合法性，并激活账号
    因为有账号才能拿到token，故不考虑，账号不存在的情况
    :return: json
    """
    try:
        validate = validate_token(get_token(), 'EMAIL_TOKEN')
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})

    # 验证账号是否激活
    user = User.query.get(validate['id'])
    if user is not None:
        return jsonify({'code': '2000', 'message': '该账号已激活'})

    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)

    try:  # 从 Redis 读取注册信息
        name = r.hget(validate['id'], 'name').decode('UTF-8')
        password = r.hget(validate['id'], 'password').decode('UTF-8')
        room_id = r.hget(validate['id'], 'roomId').decode('UTF-8')
        email = r.hget(validate['id'], 'email').decode('UTF-8')
    except AttributeError:
        return jsonify({'code': '2000', 'message': '注册信息已过期'})

    user = User(id=validate['id'], name=name, password=password, room_id=room_id, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({'adopt': True, 'message': 'success'})
