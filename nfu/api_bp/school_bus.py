from json import dumps, loads
from os import getenv

from flask import Blueprint, g, jsonify, render_template, request, send_file

from nfu.common import check_access_token, check_power_school_bus
from nfu.expand import school_bus
from nfu.expand.school_bus import get_not_used_order
from nfu.expand.token import validate_token
from nfu.models import User
from nfu.NFUError import NFUError

school_bus_bp = Blueprint('school_bus', __name__)


@school_bus_bp.route('/schedule', methods=['POST'])
@check_access_token
@check_power_school_bus
def get_schedule():
    """
    获取班车时刻表
    :return:
    """

    try:
        data = loads(request.get_data().decode("utf-8"))
        route_id = int(data['route_id'])
        date = data['date']
    except (TypeError, ValueError):
        return jsonify({'adopt': False, 'message': '服务器内部错误'})

    try:
        return jsonify({'adopt': True, 'message': school_bus.get_bus_schedule(route_id, date, g.user.bus_session)})
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})


@school_bus_bp.route('/passenger')
@check_access_token
@check_power_school_bus
def get_passenger():
    """
    获取乘车人数据
    :return:
    """

    try:
        return jsonify({'adopt': True, 'message': school_bus.get_passenger_data(g.user.bus_session)})
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})


@school_bus_bp.route('/order/create', methods=['POST'])
@check_access_token
@check_power_school_bus
def create_order_bp():
    """
    买票
    :return:
    """
    try:
        data = loads(request.get_data().decode("utf-8"))
        passenger_ids = data['passenger_ids']
        connect_id = data['passenger_ids'][0]
        passenger_ids = dumps(passenger_ids)[1:-1]
        schedule_id = data['schedule_id']
        date = data['date']
        take_station = data['take_station']
        bus_session = g.user.bus_session
    except ValueError:
        return jsonify({'adopt': False, 'message': '服务器内部错误'})

    try:
        order = school_bus.create_order(passenger_ids, connect_id, schedule_id, date, take_station, bus_session)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message, 'code': err.code})

    return jsonify({
        'adopt': True,
        'message': order,
        'alipays_url': school_bus.get_alipays_url(order['trade_no']),
        'alipays_qr_url': getenv('API_URL') + '/school-bus/alipay/qrcode?trade_no=' + order['trade_no']
    })


@school_bus_bp.route('/ticket-id', methods=['POST'])
@check_access_token
@check_power_school_bus
def get_ticket_ids_bp():
    """
    获取车票的id，用于退票
    :return:
    """
    try:
        data = loads(request.get_data().decode("utf-8"))
        order_id = data['order_id']
    except ValueError:
        return jsonify({'adopt': False, 'message': '服务器内部错误'})

    try:
        return jsonify({'adopt': True, 'message': school_bus.get_ticket_ids(order_id, g.user.bus_session)})
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})


@school_bus_bp.route('/ticket/delete', methods=['POST'])
@check_access_token
@check_power_school_bus
def return_ticket_bp():
    """
    退票
    :return:
    """

    try:
        data = loads(request.get_data().decode("utf-8"))
        order_id = data['order_id']
        ticket_id = data['ticket_id']
    except ValueError:
        return jsonify({'adopt': False, 'message': '服务器内部错误'})

    try:
        return jsonify({'adopt': True, 'message': school_bus.return_ticket(order_id, ticket_id, g.user.bus_session)})
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})


@school_bus_bp.route('/order/not-used')
@check_access_token
@check_power_school_bus
def not_used_order():
    """
    获取待乘车的订单
    :return:
    """
    try:
        return jsonify({'adopt': True, 'message': get_not_used_order(g.user.bus_session)})
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})


@school_bus_bp.route('/ticket')
def get_ticket():
    """
    获取电子车票
    :return:
    """

    try:
        token_data = validate_token(request.args.get('token'))
    except NFUError as err:
        return render_template('html/err.html', err=err.message)

    if not token_data['school_bus']:
        return render_template('html/err.html', err='没有访问权限')

    user = User.query.get(token_data['id'])
    order_id = request.args.get('order-id')

    try:
        ticket_data = school_bus.get_ticket_data(order_id, user.bus_session)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})

    return render_template(
        'html/bus_ticket.html',
        bus_data=ticket_data[0],
        ticket=ticket_data[1],
        javascript=ticket_data[2]
    )


@school_bus_bp.route('/alipay')
def alipay():
    """
    调起支付宝支付
    :return:
    """
    return render_template('html/alipay.html', trade_no=request.args.get('trade_no'))


@school_bus_bp.route('/alipay/qrcode')
def alipay_qrcode():
    """
    二维码生成
    :return:
    """
    alipays_url = school_bus.get_alipays_url(request.args.get('trade_no'))
    return send_file(school_bus.get_qrcode(url=alipays_url), mimetype='image/png')
