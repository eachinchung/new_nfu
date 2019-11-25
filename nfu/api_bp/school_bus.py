from json import dumps, loads

from flask import Blueprint, g, jsonify, render_template, request, send_file

from nfu.common import check_access_token, check_power_school_bus
from nfu.expand import school_bus
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
        route_id = int(data['routeId'])
        date = data['date']
    except (TypeError, ValueError):
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    try:
        return jsonify({'code': '1000', 'message': school_bus.get_bus_schedule(route_id, date, g.user.bus_session)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@school_bus_bp.route('/passenger')
@check_access_token
@check_power_school_bus
def get_passenger():
    """
    获取乘车人数据
    :return:
    """

    try:
        return jsonify({'code': '1000', 'message': school_bus.get_passenger_data(g.user.bus_session)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


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
        passenger_ids = data['passengerIds']
        connect_id = data['passengerIds'][0]
        passenger_ids = dumps(passenger_ids)[1:-1]
        schedule_id = data['scheduleId']
        date = data['date']
        take_station = data['takeStation']
        bus_session = g.user.bus_session
    except ValueError:
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    try:
        order = school_bus.create_order(passenger_ids, connect_id, schedule_id, date, take_station, bus_session)
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message, 'busCode': err.code})

    return jsonify({
        'code': '1000',
        'message': order
    })


@school_bus_bp.route('/order/pay', methods=['POST'])
@check_access_token
@check_power_school_bus
def order_pay():
    """
    订单的支付信息
    :return:
    """
    try:
        data = loads(request.get_data().decode("utf-8"))
        order_id = data['orderId']
        bus_session = g.user.bus_session
    except ValueError:
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    return jsonify({
        'code': '1000',
        'message': school_bus.get_pay_order(order_id, bus_session)
    })


@school_bus_bp.route('/ticketId', methods=['POST'])
@check_access_token
@check_power_school_bus
def get_ticket_ids_bp():
    """
    获取车票的id，用于退票
    :return:
    """
    try:
        data = loads(request.get_data().decode('utf-8'))
        order_id = data['orderId']
    except ValueError:
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    try:
        return jsonify({'code': '1000', 'message': school_bus.get_ticket_ids(order_id, g.user.bus_session)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@school_bus_bp.route('/ticket/delete', methods=['POST'])
@check_access_token
@check_power_school_bus
def return_ticket_bp():
    """
    退票
    :return:
    """

    try:
        data = loads(request.get_data().decode('utf-8'))
        order_id = data['orderId']
        ticket_id = data['ticketId']
    except ValueError:
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    try:
        return jsonify({'code': '1000', 'message': school_bus.return_ticket(order_id, ticket_id, g.user.bus_session)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@school_bus_bp.route('/order/notUsed')
@check_access_token
@check_power_school_bus
def not_used_order():
    """
    获取待乘车的订单
    :return:
    """
    try:
        return jsonify({'code': '1000', 'message': school_bus.get_not_used_order(g.user.id, g.user.bus_session)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@school_bus_bp.route('/ticket/<string:token>')
def get_ticket(token: str) -> render_template:
    """
    获取电子车票
    :return:
    """

    try:
        token_data = validate_token(token, 'TICKET_TOKEN')
        user_id = token_data['userId']
        order_id = token_data['orderId']
    except NFUError as err:
        return render_template('html/err.html', err=err.message)

    user = User.query.get(user_id)

    try:
        ticket_data = school_bus.get_ticket_data(order_id, user.bus_session)
    except NFUError as err:
        return render_template('html/err.html', err=err.message)

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
    return render_template('html/alipay.html', trade_no=request.args.get('tradeNo'))


@school_bus_bp.route('/alipay/qrcode')
def alipay_qrcode():
    """
    二维码生成
    :return:
    """
    alipay_url = school_bus.get_alipay_url(request.args.get('tradeNo'))
    return send_file(school_bus.get_qrcode(url=alipay_url), mimetype='image/png')
