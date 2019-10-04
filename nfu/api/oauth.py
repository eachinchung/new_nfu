from flask import Blueprint, jsonify, request

from nfu.email import send_validate_email
from nfu.extensions import db
from nfu.models import User, Power
from nfu.nfu import get_student_name
from nfu.token import generate_token, validate_token

oauth_bp = Blueprint('oauth', __name__)


@oauth_bp.route('/token/get', methods=['POST'])
def get_token():
    """
    登陆接口，获取令牌
    return: json
    """
    user_id = request.form.get('user_id')
    password = request.form.get('password')

    # 首先验证账号是否存在
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': '账号不存在。'}), 500

    if not user.validate_password(password):
        return jsonify({'message': '密码错误'}), 500

    # 验证账号是否激活，若账号未激活，往后操作无意义
    user_power = Power.query.get(user_id)
    if not user_power.validate_email:
        data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        }
        return jsonify({
            'message': '账号暂未激活。',
            'refresh_email_token': generate_token(data, token_type='REFRESH_EMAIL_TOKEN')
        })

    return jsonify({
        'message': 'success',
        'access_token': generate_token(user_power.get_dict()),
        'refresh_token': generate_token({'id': user.id}, token_type='REFRESH_TOKEN', expires_in=2592000)
    })


@oauth_bp.route('/token/refresh', methods=['POST'])
def refresh_token():
    """
    刷新令牌
    :return: json
    """
    token = request.form.get('refresh_token')
    validate = validate_token(token, 'REFRESH_TOKEN')

    # 令牌验证不通过
    if not validate[0]:
        return jsonify({'message': validate[1]}), 403

    user = User.query.get(validate[1]['user_id'])
    user_power = Power.query.get(validate[1]['user_id'])

    if user is None:
        return jsonify({'message': '账号不存在'}), 500

    return jsonify({
        'message': 'success',
        'access_token': generate_token(user_power.get_dict()),
        'refresh_token': generate_token({'id': user.id}, token_type='REFRESH_TOKEN', expires_in=2592000)
    })


@oauth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    """
    注册接口
    :return: json
    """
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    room_id = request.form.get('room_id')
    email = request.form.get('email')

    user = User.query.get(user_id)
    if user is not None:
        return jsonify({'message': '该账号已存在'}), 500

    # 如果正确获得学生姓名，默认代表该用户拥有该账号合法性
    name = get_student_name(user_id, password)
    if not name[0]:
        return jsonify({'message': name[1]}), 500

    token = generate_token({'id': user_id}, token_type='EMAIL_TOKEN')
    send_validate_email(email, name[1], user_id, token)

    user = User(id=user_id, name=name[1], room_id=room_id, email=email)
    user.set_password(password)  # 将教务系统密码默认为用户密码，并哈希加密

    db.session.add(user)
    db.session.add(Power(id=user_id))  # 初始化权限，全部False
    db.session.commit()

    return jsonify({'message': 'success'})


@oauth_bp.route('/refresh_validate_email', methods=['POST'])
def refresh_validate_email():
    """
    重新发送激活邮件
    :return: json
    """
    token = request.form.get('refresh_validate_email_token')
    validate = validate_token(token, 'REFRESH_EMAIL_TOKEN')

    # 令牌验证不通过
    if not validate[0]:
        return jsonify({'message': validate[1]}), 403

    user_power = Power.query.get(validate[1]['id'])

    if user_power is None:
        return jsonify({'message': '账号不存在'}), 500

    if user_power.validate_email:
        return jsonify({'message': '该账号已激活'}), 500

    token = generate_token({'id': validate[1]['id']}, token_type='EMAIL_TOKEN')
    send_validate_email(validate[1]['email'], validate[1]['name'], validate[1]['id'], token)
    return jsonify({'message': 'success'})
