from datetime import datetime

from flask import Blueprint, g, jsonify, make_response, redirect, request

from nfu.decorators import check_access_token
from nfu.electric import ElectricPay, get_electric_data
from nfu.extensions import db
from nfu.models import Dormitory, Electric

electric_bp = Blueprint('electric', __name__)


@electric_bp.route('/get', methods=['POST'])
@check_access_token
def get():
    """
    获取宿舍电费
    :return: json
    """

    electric_data = Electric.query.filter_by(room_id=g.user.room_id).order_by(Electric.time.desc()).first()

    # 当数据库没有电费数据时，我们向安心付请求数据
    if electric_data is None:
        electric = get_electric_data(g.user.room_id)

        if not electric[0]:
            return jsonify({'adopt': False, 'message': electric[1]}), 500

        # 并将电费数据写入数据库
        electric_data = Electric(room_id=g.user.room_id, value=electric[1], time=datetime.now())
        db.session.add(electric_data)
        db.session.commit()

    return jsonify({'adopt': True, 'message': electric_data.value})


@electric_bp.route('/create_order', methods=['POST'])
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
    order_data = order.create_order()

    if not order_data[0]:
        return jsonify({'adopt': False, 'message': order_data[1]}), 500

    return jsonify({
        'adopt': True,
        'message': {
            'json': order_data[1],
            'signature': order_data[2],
            'electric_cookies': order_data[3]
        }
    })


@electric_bp.route('/pay_order')
@check_access_token
def pay_order():
    """
    跳转支付页面
    :return:
    """
    json_data = request.args.get('json')
    signature = request.args.get('signature')
    electric_cookies = request.args.get('electric_cookies')
    url = "http://nfu.zhihuianxin.net/school_paycgi_wxpay/paycgi_upw?json=" + json_data + "&signature=" + signature
    response = make_response(redirect(url))
    response.set_cookie('JSESSIONID', electric_cookies)
    return response
