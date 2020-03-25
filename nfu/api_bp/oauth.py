from hashlib import md5
from json import loads
from os import getenv
from random import sample
from string import ascii_letters, digits

from flask import Blueprint, jsonify, redirect, render_template, request
from redis import Redis
from requests import get
from werkzeug.security import generate_password_hash

from nfu.common import get_token
from nfu.expand.email import send_validate_email
from nfu.expand.nfu import get_student_name
from nfu.expand.token import create_access_token, generate_token, validate_token, write_access_token_redis_cache
from nfu.extensions import db
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
    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)

    if user is None:  # 当MySql为空时

        # 查看缓存是否有已注册的信息
        if r.hget(f"sign-up-{user_id}", 'name') is None:
            return jsonify({'code': '0001', 'message': '南苑聚合账号不存在'})

        else:
            return jsonify({'code': '0002', 'message': '账号暂未激活'})

    if not user.validate_password(data['password']):
        return jsonify({'code': '0003', 'message': '密码错误'})

    dormitory, bus_power = write_access_token_redis_cache(r, user)

    return jsonify(create_access_token(user, dormitory, bus_power))


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

    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)

    try:  # 从 Redis 读取信息
        name = r.hget(f"user-{validate['id']}", 'name').decode('utf-8')
        room_id = int(r.hget(f"user-{validate['id']}", 'roomId').decode('utf-8'))
        email = r.hget(f"user-{validate['id']}", 'email').decode('utf-8')
        dormitory = r.hget(f"user-{validate['id']}", 'dormitory').decode('utf-8')
        bus_power = int(r.hget(f"user-{validate['id']}", 'busPower'))
    except AttributeError:
        user = User.query.get(validate['id'])
        dormitory, bus_power = write_access_token_redis_cache(r, user)
    else:
        user = User(id=validate['id'], name=name, room_id=room_id, email=email)

    return jsonify(create_access_token(user, dormitory, bus_power))


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
    r.hmset(f"sign-up-{user_id}", {
        'name': name,
        'password': generate_password_hash(password),
        'roomId': room_id,
        'email': email
    })

    # 设置缓存一小时过期
    r.expire(user_id, 3600)

    return jsonify({'code': '1000', 'message': '激活邮件已发送至您的邮箱，请查看'})


@oauth_bp.route('/nfuca')
def nfuca() -> jsonify:
    """
    从计协获取用户信息
    :return:
    """
    try:
        url = 'https://api.nfuca.com/openLoginGetInfo'

        data = dict(request.args)
        data['sign'] = md5(f'{data["name"]}{data["time"]}{data["openid"]}{data["nonce"]}{getenv("NFUCA_KEY")}'
                           .encode(encoding='UTF-8')).hexdigest()

        response = get(url, params=data, timeout=10)
        nfuca_data = loads(response.text)

        if nfuca_data['code'] != 0:
            return render_template('html/err.html', err=nfuca_data['msg'])

        if nfuca_data['data']['no'] is None:
            return render_template('html/err.html', err='请前往南苑计协公众号，注册南苑计协账号')

        oauth_id = f'{nfuca_data["data"]["no"]}-{"".join(sample(ascii_letters + digits, 10))}'

    except OSError:
        return render_template('html/err.html', err='计协服务器繁忙')
    except KeyError:
        return render_template('html/err.html', err='提交信息不合法')

    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)

    user = User.query.get(nfuca_data["data"]["no"])
    if user is None:  # 当MySql为空时
        r.set(oauth_id, response.text, ex=3600)
        return redirect(f"{getenv('FRONT_END_URL')}/oauth/nfuca/sign-up?sign={oauth_id}")

    if user.open_id is None:
        user.open_id = data["openid"]
        db.session.add(user)
        db.session.commit()

    r.set(oauth_id, nfuca_data["data"]["no"], ex=30)
    return redirect(f"{getenv('FRONT_END_URL')}/oauth/nfuca?sign={oauth_id}")


@oauth_bp.route('/nfuca/login', methods=['POST'])
def nfuca_login() -> jsonify:
    """
    计协登录
    :return:
    """
    try:
        sign = loads(request.get_data().decode('utf-8'))['sign']
    except ValueError:
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)
    user_id = r.get(sign).decode('utf-8')
    r.delete(sign)

    if user_id is None:
        return jsonify({'code': '2000', 'message': '签名已过期'})

    try:  # 从 Redis 读取信息
        name = r.hget(f"user-{user_id}", 'name').decode('utf-8')
        room_id = int(r.hget(f"user-{user_id}", 'roomId').decode('utf-8'))
        email = r.hget(f"user-{user_id}", 'email').decode('utf-8')
        dormitory = r.hget(f"user-{user_id}", 'dormitory').decode('utf-8')
        bus_power = int(r.hget(f"user-{user_id}", 'busPower'))
    except AttributeError:
        user = User.query.get(user_id)
        dormitory, bus_power = write_access_token_redis_cache(r, user)
    else:
        user = User(id=user_id, name=name, room_id=room_id, email=email)

    return jsonify(create_access_token(user, dormitory, bus_power))


@oauth_bp.route('/nfuca/sign-up', methods=['POST'])
def nfuca_sign_up() -> jsonify:
    """
    计协注册
    :return:
    """
    try:
        data = loads(request.get_data().decode('utf-8'))
        sign = data['sign']
        room_id = data['roomId']
        email = data['email']
    except (TypeError, ValueError):
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)
    user_data = r.get(sign).decode('utf-8')
    r.delete(sign)

    if user_data is None:
        return jsonify({'code': '2000', 'message': '签名已过期'})

    user_data = loads(user_data)['data']
    user = User.query.get(user_data['no'])
    if user is not None:
        return jsonify({'code': '2000', 'message': '该账号已存在'})

    token = generate_token({'id': user_data['no']}, token_type='EMAIL_TOKEN')
    send_validate_email(email, user_data['name'], user_data['no'], token)

    # 把帐号资料写入缓存
    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)
    r.hmset(f"sign-up-{user_data['no']}", {
        'name': user_data['name'],
        'password': generate_password_hash(user_data['pwd']),
        'roomId': room_id,
        'email': email
    })

    # 设置缓存一小时过期
    r.expire(user_data['no'], 3600)
    return jsonify({'code': '1000', 'message': '激活邮件已发送至您的邮箱，请查看'})
