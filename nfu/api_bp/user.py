from datetime import datetime
from json import decoder, loads
from os import getenv

from flask import Blueprint, g, jsonify, render_template, request
from redis import Redis
from requests import post
from werkzeug.security import generate_password_hash

from nfu.common import check_access_token, verification_code
from nfu.expand.nfu import get_jw_token, get_profile
from nfu.extensions import db
from nfu.models import College, Profession, Profile, User
from nfu.nfu_error import NFUError

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile')
@check_access_token
def get_profile_api():
    """
    获取学生个人信息
    :return:
    """
    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)

    try:
        # 首先向 Redis 读取缓存
        grade = r.hget(f"profile-{g.user.id}", 'grade').decode('utf-8')
        college = r.hget(f"profile-{g.user.id}", 'college').decode('utf-8')
        profession = r.hget(f"profile-{g.user.id}", 'profession').decode('utf-8')
        direction = r.hget(f"profile-{g.user.id}", 'direction').decode('utf-8')

    except AttributeError:

        # 向 MySQL 读取缓存
        profile = Profile.query.get(g.user.id)

        if profile is None:

            try:
                token = get_jw_token(g.user.id)
                profile_data = get_profile(g.user.id, token)

            except NFUError as err:
                return jsonify({'code': err.code, 'message': err.message})

            else:
                profile = Profile(
                    user_id=g.user.id,
                    grade=profile_data['grade'],
                    college_id=profile_data['college_id'],
                    profession_id=profile_data['profession_id'],
                    direction=profile_data['direction']
                )

                db.session.add(profile)
                db.session.commit()

            grade = profile_data['grade']
            college = College.query.get(profile_data['college_id']).college
            profession = Profession.query.get(profile_data['profession_id']).profession
            direction = profile_data['direction']

            r.hmset(f"profile-{g.user.id}", {
                'grade': grade,
                'college': college,
                'profession': profession,
                'direction': direction
            })

        else:
            grade = profile.grade
            college = College.query.get(profile.college_id).college
            profession = Profession.query.get(profile.profession_id).profession
            direction = profile.direction

            r.hmset(f"profile-{g.user.id}", {
                'grade': grade,
                'college': college,
                'profession': profession,
                'direction': direction
            })

    return jsonify({'code': '2000', 'message': {
        'grade': grade,
        'college': college,
        'profession': profession,
        'direction': direction
    }})


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
    user = User.query.get(g.user.id)
    user.room_id = int(data['roomId'])
    db.session.add(user)
    db.session.commit()

    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)
    r.delete(f"user-{g.user.id}")

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

    user = User.query.get(g.user.id)
    if not user.validate_password(password):
        return jsonify({'code': '0003', 'message': '密码错误'})

    try:  # 验证验证码是否正确
        verification_code(code)
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})

    user.password = generate_password_hash(new_password)
    db.session.add(user)
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

    user = User.query.get(g.user.id)
    if not user.validate_password(password):
        return jsonify({'code': '2000', 'message': '密码错误'})

    try:  # 验证验证码是否正确
        verification_code(code)
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})

    user.email = new_email
    db.session.add(user)
    db.session.commit()

    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)
    r.delete(f"user-{g.user.id}")

    return jsonify({'code': '1000', 'message': '邮箱更新成功'})
