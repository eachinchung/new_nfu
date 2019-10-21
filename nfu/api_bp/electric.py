from datetime import datetime

from flask import Blueprint, g, jsonify, make_response, redirect, request

from nfu.common import check_access_token
from nfu.expand.electric import ElectricPay, get_electric_create_log, get_electric_data
from nfu.expand.token import validate_token
from nfu.extensions import db
from nfu.models import Dormitory, Electric
from nfu.NFUError import NFUError

electric_bp = Blueprint('electric', __name__)


@electric_bp.route('/get')
@check_access_token
def get():
    """
    获取宿舍电费
    :return: json
    """

    electric_data = Electric.query.filter_by(room_id=g.user.room_id).order_by(Electric.time.desc()).first()

    # 当数据库没有电费数据时，我们向安心付请求数据
    if electric_data is None:
        try:
            electric = get_electric_data(g.user.room_id)
        except NFUError as err:
            return jsonify({'adopt': False, 'message': err.message}), 500

        # 并将电费数据写入数据库
        electric_data = Electric(room_id=g.user.room_id, value=electric, time=datetime.now())
        db.session.add(electric_data)
        db.session.commit()

    return jsonify({'adopt': True, 'message': electric_data.value})


@electric_bp.route('/analyse')
@check_access_token
def analyse():
    """
    分析近15天电费
    :return:
    """
    electric_data = Electric.query.filter_by(room_id=g.user.room_id).order_by(Electric.time.desc()).limit(15).all()

    if electric_data is None:
        return jsonify({'adopt': False, 'message': '当前宿舍没有电费数据'}), 500

    electric_list = []
    for electric in electric_data:
        electric_list.append({
            'date': str(electric.time),
            'electric': electric.value
        })

    return jsonify({'adopt': True, 'message': electric_list})


@electric_bp.route('/order/log', methods=['POST'])
@check_access_token
def create_log():
    """
    电费充值记录
    :return:
    """
    page = request.form.get('page')

    try:
        electric_create_log = get_electric_create_log(g.user.room_id, page)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 500
    else:
        return jsonify({'adopt': True, 'message': electric_create_log})


@electric_bp.route('/order/create', methods=['POST'])
@check_access_token
def create_order():
    """
    创建电费充值订单
    :return: json 跳转支付页面所必须的数据
    """

    amount = request.form.get('amount')
    dormitory = Dormitory.query.get(g.user.room_id)

    order = ElectricPay(
        amount, g.user.id, g.user.name, g.user.room_id, dormitory.building, dormitory.floor, dormitory.room)

    try:
        order_data = order.create_order()
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 500

    return jsonify({
        'adopt': True,
        'message': {
            'json': order_data[0],
            'signature': order_data[1],
            'electric_cookies': order_data[2]
        }
    })


@electric_bp.route('/order/pay')
def pay_order():
    """
    跳转支付页面
    :return:
    """

    try:
        validate_token(request.args.get('token'))
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 403

    json_data = request.args.get('json')
    signature = request.args.get('signature')
    electric_cookies = request.args.get('electric_cookies')

    url = "http://nfu.zhihuianxin.net/school_paycgi_wxpay/paycgi_upw?json=" + json_data + "&signature=" + signature
    response = make_response(redirect(url))
    response.set_cookie('JSESSIONID', electric_cookies)
    return response
