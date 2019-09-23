from flask import Blueprint, request, jsonify

from nfu.expand import generate_token, validate_token, send_email
from nfu.extensions import db
from nfu.models import User
from nfu.nfu_expand import get_student_name

oauth_bp = Blueprint('oauth', __name__)


# 登陆接口，获取令牌
@oauth_bp.route('/get_token', methods=['POST'])
def get_token():
    user_id = request.form.get('user_id')
    password = request.form.get('password')

    send_email('验证你的邮箱', ['eachin@kaimon.cn'], '测试')

    user = User.query.get(user_id)
    if user is None or not user.validate_password(password):
        return jsonify({'message': '账号或密码错误'})

    return jsonify({
        'message': 'success',
        'access_token': generate_token({'id': user.id}),
        'refresh_token': generate_token({'id': user.id}, token_type='REFRESH_TOKEN', expires_in=2592000)
    })


# 注册接口
@oauth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    room_id = request.form.get('room_id')
    email = request.form.get('email')

    name = get_student_name(user_id, password)

    if name[0]:
        user = User(id=user_id, name=name[1], room_id=room_id, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # send_email('验证你的邮箱', [email], '测试')

        return jsonify({'message': 'success'})

    else:
        return jsonify({'message': name[1]})


# 刷新令牌
@oauth_bp.route('/refresh_token', methods=['POST'])
def refresh_token():
    token = request.form.get('refresh_token')
    validate = validate_token(token, 'REFRESH_TOKEN')
    if validate[0]:
        return jsonify({
            'message': 'success',
            'access_token': generate_token(validate[1]),
            'refresh_token': generate_token(validate[1], token_type='REFRESH_TOKEN', expires_in=2592000)
        })
    else:
        return jsonify({'message': validate[1]})
