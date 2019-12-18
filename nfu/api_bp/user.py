from datetime import datetime
from json import loads, decoder
from os import getenv

from flask import Blueprint, g, jsonify, render_template, request
from requests import post
from werkzeug.security import generate_password_hash

from nfu.common import check_access_token, verification_code
from nfu.extensions import db
from nfu.models import Dormitory
from nfu.nfu_error import NFUError

user_bp = Blueprint('user', __name__)


@user_bp.route('/data')
@check_access_token
def get_user():
    """
    获取用户数据
    :return:
    """
    dormitory = Dormitory.query.get(g.user.room_id)
    return jsonify({
        'code': '1000',
        'name': g.user.name,
        'email': g.user.email,
        'dormitory': f'{dormitory.building} {dormitory.floor} {dormitory.room}'
    })


@user_bp.route('/feedback', methods=['POST'])
@check_access_token
def feedback():
    """
    意见反馈
    """
    try:
        data = loads(request.get_data().decode('utf-8'))
        title = data['title']
        feedback_data = data['feedback']
    except (TypeError, ValueError):
        return jsonify({'code': '2000', 'message': '请求数据错误'})

    url = f'https://sc.ftqq.com/{getenv("SCKEY")}.send'
    data = {
        'text': '南苑聚合意见反馈',
        'desp': render_template(
            'markdown/feedback.md',
            name=g.user.name,
            email=g.user.email,
            title=title,
            feedback=feedback_data,
            date=datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        )
    }

    try:
        response = post(url, data=data)
        errmsg = loads(response.text)['errmsg']
    except (OSError, KeyError, decoder.JSONDecodeError):
        return jsonify({'code': '2000', 'message': '与 Server酱 连接失败'})

    if errmsg == 'success':
        return jsonify({'code': '1000', 'message': 'success'})
    else:
        return jsonify({'code': '2000', 'message': errmsg})


@user_bp.route('/set/dormitory', methods=['POST'])
@check_access_token
def set_dormitory():
    """
    更新宿舍信息
    :return:
    """
    data = loads(request.get_data().decode('utf-8'))
    room_id = int(data['roomId'])
    g.user.room_id = room_id
    db.session.add(g.user)
    db.session.commit()

    return jsonify({'code': '1000', 'message': 'success'})


@user_bp.route('/set/password', methods=['POST'])
@check_access_token
def set_password() -> jsonify:
    """
    更新密码
    :return:
    """
    try:
        data = loads(request.get_data().decode('utf-8'))
        new_password = data['newPassword']
        password = data['password']
        code = int(data['code'])
    except (TypeError, ValueError):
        return jsonify({'code': '2000', 'message': '请求数据错误'})

    if not g.user.validate_password(password):
        return jsonify({'code': '0003', 'message': '密码错误'})

    try:  # 验证验证码是否正确
        verification_code(code)
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})

    g.user.password = generate_password_hash(new_password)
    db.session.add(g.user)
    db.session.commit()

    return jsonify({'code': '1000', 'message': '密码更新成功'})


@user_bp.route('/set/email', methods=['POST'])
@check_access_token
def set_email() -> jsonify:
    """
    更新邮箱
    :return:
    """
    try:
        data = loads(request.get_data().decode('utf-8'))
        password = data['password']
        new_email = data['newEmail']
        code = int(data['code'])
    except (TypeError, ValueError):
        return jsonify({'code': '2000', 'message': '请求数据错误'})

    if not g.user.validate_password(password):
        return jsonify({'code': '2000', 'message': '密码错误'})

    try:  # 验证验证码是否正确
        verification_code(code)
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})

    g.user.email = new_email
    db.session.add(g.user)
    db.session.commit()

    return jsonify({'code': '1000', 'message': '邮箱更新成功'})
