from json import loads

from flask import Blueprint, jsonify, request

from nfu.common import get_token
from nfu.expand.email import send_validate_email
from nfu.expand.nfu import get_student_name
from nfu.expand.token import generate_token, validate_token
from nfu.extensions import db
from nfu.models import Power, User
from nfu.NFUError import NFUError

oauth_bp = Blueprint('oauth', __name__)


@oauth_bp.route('/token/get', methods=['POST'])
def get_token_bp():
    """
    登陆接口，获取令牌
    return: json
    """

    try:
        data = loads(request.get_data().decode("utf-8"))
        user_id = int(data['user_id'])
    except (TypeError, ValueError):
        return jsonify({'adopt': False, 'code': 1002, 'message': '账号不存在'})

    # 首先验证账号是否存在
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'adopt': False, 'code': 1002, 'message': '账号不存在'})

    if not user.validate_password(data['password']):
        return jsonify({'adopt': False, 'code': 1003, 'message': '密码错误'})

    # 验证账号是否激活，若账号未激活，往后操作无意义
    user_power = Power.query.get(user_id)
    if not user_power.validate_email:
        data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        }
        return jsonify({
            'adopt': False,
            'code': 1001,
            'message': '账号暂未激活。',
            'refresh_email_token': generate_token(data, token_type='REFRESH_EMAIL_TOKEN')
        })

    return jsonify({
        'adopt': True,
        'message': {
            'access_token': generate_token(user_power.get_dict()),
            'refresh_token': generate_token({'id': user.id}, token_type='REFRESH_TOKEN', expires_in=2592000)
        }
    })


@oauth_bp.route('/token/refresh')
def refresh_token():
    """
    刷新令牌
    :return: json
    """

    # 验证 token 是否通过
    try:
        validate = validate_token(get_token(), 'REFRESH_TOKEN')
    except ValueError as err:
        return jsonify({'adopt': False, 'message': str(err)})

    user = User.query.get(validate['id'])
    user_power = Power.query.get(validate['id'])

    if user is None:
        return jsonify({'adopt': False, 'message': '账号不存在'})

    return jsonify({
        'adopt': True,
        'message': {
            'access_token': generate_token(user_power.get_dict()),
            'refresh_token': generate_token({'id': user.id}, token_type='REFRESH_TOKEN', expires_in=2592000)
        }
    })


@oauth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    """
    注册接口
    :return: json
    """
    try:
        data = loads(request.get_data().decode("utf-8"))
        user_id = int(data['user_id'])
        password = data['password']
        room_id = data['room_id']
        email = data['email']
    except (TypeError, ValueError):
        return jsonify({'adopt': False, 'message': '服务器内部错误'})

    # 防一波教务系统bug。。。
    if password is None or password == '':
        return jsonify({'adopt': False, 'message': '密码不能为空'})

    user = User.query.get(user_id)
    if user is not None:
        return jsonify({'adopt': False, 'message': '该账号已存在'})

    # 如果正确获得学生姓名，默认代表该用户拥有该账号合法性
    try:
        name = get_student_name(user_id, password)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})

    token = generate_token({'id': user_id}, token_type='EMAIL_TOKEN')
    send_validate_email(email, name, user_id, token)

    user = User(id=user_id, name=name, room_id=room_id, email=email)
    user.set_password(password)  # 将教务系统密码默认为用户密码，并哈希加密

    db.session.add(user)
    db.session.commit()

    # 初始化权限，全部False
    db.session.add(Power(id=user_id))
    db.session.commit()

    return jsonify({'adopt': True, 'message': 'success'})


@oauth_bp.route('/refresh_validate_email')
def refresh_validate_email():
    """
    重新发送激活邮件
    :return: json
    """

    try:
        validate = validate_token(get_token(), 'REFRESH_EMAIL_TOKEN')
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})

    user_power = Power.query.get(validate['id'])

    if user_power is None:
        return jsonify({'adopt': False, 'message': '账号不存在'})

    if user_power.validate_email:
        return jsonify({'adopt': False, 'message': '该账号已激活'})

    token = generate_token({'id': validate['id']}, token_type='EMAIL_TOKEN')
    send_validate_email(validate['email'], validate['name'], validate['id'], token)
    return jsonify({'adopt': True, 'message': 'success'})
