from json import loads

from flask import Blueprint, g, jsonify, request, send_file

from nfu.common import check_access_token
from nfu.expand.electric import ElectricPay, get_electric_log
from nfu.expand_bus.ticket import get_qrcode
from nfu.models import Dormitory, Electric
from nfu.nfu_error import NFUError

electric_bp = Blueprint('electric', __name__)


@electric_bp.route('/get')
@check_access_token
def get():
    """
    获取宿舍电费
    :return: json
    """

    electric_data = Electric.query.filter_by(room_id=g.user.room_id).order_by(Electric.date.desc()).first()
    return jsonify({
        'code': '1000',
        'electric': electric_data.value,
        'date': electric_data.date.strftime("%Y-%m-%d")
    })


@electric_bp.route('/analyse')
@check_access_token
def analyse():
    """
    分析近15天电费
    :return:
    """
    electric_data = Electric.query.filter_by(room_id=g.user.room_id).order_by(Electric.date.desc()).limit(15).all()

    if electric_data is None:
        return jsonify({'code': '2000', 'message': '当前宿舍没有电费数据'})

    electric_list = []
    for electric in electric_data:
        electric_list.append({
            'date': str(electric.time),
            'electric': electric.value
        })

    return jsonify({'code': '1000', 'message': electric_list})


@electric_bp.route('/order/log', methods=['POST'])
@check_access_token
def electric_log():
    """
    电费充值记录
    :return:
    """
    try:
        data = loads(request.get_data().decode('utf-8'))
        page = data['page']
    except ValueError:
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    try:
        return jsonify({'code': '1000', 'message': get_electric_log(g.user.room_id, page)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@electric_bp.route('/order/create', methods=['POST'])
@check_access_token
def create_order():
    """
    创建电费充值订单
    :return: json 跳转支付页面所必须的数据
    """

    try:
        data = loads(request.get_data().decode('utf-8'))
        amount = data['amount']
        dormitory = Dormitory.query.get(g.user.room_id)
    except ValueError:
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    order = ElectricPay(
        amount=amount,
        user_id=g.user.id,
        name=g.user.name,
        room_id=g.user.room_id,
        building=dormitory.building,
        floor=dormitory.floor,
        room=dormitory.room
    )

    try:
        pay_url = order.create_order()
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})

    return jsonify({
        'code': '1000',
        'wechatPay': pay_url
    })


@electric_bp.route('/wechat-pay/qrcode')
def wechat_pay_qrcode():
    """
    生成二维码
    """
    return send_file(get_qrcode(url=request.args.get('url')), mimetype='image/png')
