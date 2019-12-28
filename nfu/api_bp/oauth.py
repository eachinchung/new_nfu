from json import loads
from os import getenv

from flask import Blueprint, jsonify, request
from redis import Redis
from werkzeug.security import generate_password_hash

from nfu.common import get_token
from nfu.expand.email import send_validate_email
from nfu.expand.nfu import get_student_name
from nfu.expand.token import create_access_token, generate_token, validate_token
from nfu.models import User
from nfu.nfu_error import NFUError

oauth_bp = Blueprint('oauth', __name__)


@oauth_bp.route('/token', methods=['POST'])
def get_token_bp() -> jsonify:
    """
    登陆接口，获取令牌
    return: json
    """

    try:
        data = loads(request.get_data().decode('utf-8'))
        user_id = int(data['userId'])
    except (TypeError, ValueError):
        return jsonify({'code': '0004', 'message': '提交信息不合法'})

    # 首先验证账号是否存在
    user = User.query.get(user_id)

    if user is None:  # 当MySql为空时

        # 查看缓存是否有已注册的信息
        r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)

        if r.hget(user_id, 'name') is None:
            return jsonify({'code': '0001', 'message': '账号不存在，请注册'})

        else:
            return jsonify({'code': '0002', 'message': '账号暂未激活'})

    if not user.validate_password(data['password']):
        return jsonify({'code': '0003', 'message': '密码错误'})

    return jsonify(create_access_token(user))


@oauth_bp.route('/token/refresh')
def refresh_token() -> jsonify:
    """
    刷新令牌
    :return: json
    """

    # 验证 token 是否通过
    try:
        validate = validate_token(get_token(), 'REFRESH_TOKEN')
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})

    return jsonify(create_access_token(User.query.get(validate['id'])))


@oauth_bp.route('/sign-up', methods=['POST'])
def sign_up() -> jsonify:
    """
    注册接口
    :return: json
    """
    try:
        data = loads(request.get_data().decode('utf-8'))
        user_id = int(data['userId'])
        password = data['password']
        room_id = data['roomId']
        email = data['email']
    except (TypeError, ValueError):
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    # 防一波教务系统bug...
    if password is None or password == '':
        return jsonify({'code': '2000', 'message': '密码不能为空'})

    user = User.query.get(user_id)
    if user is not None:
        return jsonify({'code': '2000', 'message': '该账号已存在'})

    # 如果正确获得学生姓名，默认代表该用户拥有该账号合法性
    try:
        name = get_student_name(user_id, password)
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})

    token = generate_token({'id': user_id}, token_type='EMAIL_TOKEN')
    send_validate_email(email, name, user_id, token)

    # 把帐号资料写入缓存
    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)
    r.hmset(user_id, {
        'name': name,
        'password': generate_password_hash(password),
        'roomId': room_id,
        'email': email
    })

    # 设置缓存一小时过期
    r.expire(user_id, 3600)

    return jsonify({'code': '1000', 'message': '激活邮件已发送至您的邮箱，请查看'})
