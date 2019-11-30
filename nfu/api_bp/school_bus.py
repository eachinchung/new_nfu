from datetime import datetime
from json import dumps, loads

from flask import Blueprint, g, jsonify, render_template, request, send_file

from nfu.common import check_access_token, check_power_school_bus
from nfu.expand.token import validate_token
from nfu.expand_bus.accelerate import generate_order_number, put_mysql, put_redis
from nfu.expand_bus.order import create_order, get_pending_payment_order, get_waiting_ride_order
from nfu.expand_bus.other_data import get_bus_schedule, get_passenger_data, get_pay_order, get_ticket_ids
from nfu.expand_bus.ticket import get_alipay_url, get_qrcode, get_ticket_data, return_ticket
from nfu.models import BusUser, TicketOrder
from nfu.nfu_error import NFUError

school_bus_bp = Blueprint('school_bus', __name__)


@school_bus_bp.route('/schedule', methods=['POST'])
@check_access_token
@check_power_school_bus
def get_schedule() -> jsonify:
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
        return jsonify({'code': '1000', 'message': get_bus_schedule(route_id, date)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@school_bus_bp.route('/passenger')
@check_access_token
@check_power_school_bus
def get_passenger() -> jsonify:
    """
    获取乘车人数据
    :return:
    """

    try:
        return jsonify({'code': '1000', 'message': get_passenger_data()})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@school_bus_bp.route('/order/create', methods=['POST'])
@check_access_token
@check_power_school_bus
def create_order_bp() -> jsonify:
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

    except ValueError:
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    try:
        order = create_order(passenger_ids, connect_id, schedule_id, date, take_station)
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message, 'busCode': err.code})

    return jsonify({
        'code': '1000',
        'message': order
    })


@school_bus_bp.route('/order/pay', methods=['POST'])
@check_access_token
@check_power_school_bus
def order_pay() -> jsonify:
    """
    订单的支付信息
    :return:
    """
    try:
        data = loads(request.get_data().decode("utf-8"))
        order_id = data['orderId']

    except ValueError:
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    return jsonify({
        'code': '1000',
        'message': get_pay_order(order_id)
    })


@school_bus_bp.route('/ticketId', methods=['POST'])
@check_access_token
@check_power_school_bus
def get_ticket_ids_bp() -> jsonify:
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
        return jsonify({'code': '1000', 'message': get_ticket_ids(order_id)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@school_bus_bp.route('/ticket/delete', methods=['POST'])
@check_access_token
@check_power_school_bus
def return_ticket_bp() -> jsonify:
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
        return jsonify({'code': '1000', 'message': return_ticket(order_id, ticket_id)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@school_bus_bp.route('/order/waiting-ride')
@check_access_token
@check_power_school_bus
def waiting_ride_order() -> jsonify:
    """
    获取待乘车的订单
    :return:
    """
    try:
        return jsonify({'code': '1000', 'message': get_waiting_ride_order(g.user.id)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@school_bus_bp.route('/order/pending-payment')
@check_access_token
@check_power_school_bus
def pending_payment_order() -> jsonify:
    """
    获取待乘车的订单
    :return:
    """
    try:
        return jsonify({'code': '1000', 'message': get_pending_payment_order()})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@school_bus_bp.route('/order/create/accelerate', methods=['POST'])
@check_access_token
@check_power_school_bus
def create_accelerate_order() -> jsonify:
    """
    生成刷票订单
    :return:
    """

    try:
        data = loads(request.get_data().decode('utf-8'))
    except ValueError:
        return jsonify({'code': '2000', 'message': '服务器内部错误'})

    # 防止重复下单
    order_list = TicketOrder().query.filter_by(
        user_id=g.user.id,
        ticket_date=data['ticketDate'],
        bus_ids=data['busId']
    ).first()

    if order_list is not None:
        return jsonify({'code': '2000', 'message': '重复下单'})

    today = datetime.today()
    order_id = generate_order_number(data['orderType'], today)

    put_mysql(data, order_id, today)
    put_redis(data, order_id)

    return jsonify({'code': '1000', 'orderId': order_id})


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

    g.bus_user = BusUser.query.get(user_id)
    g.refresh = True

    try:
        ticket_data = get_ticket_data(order_id)
    except NFUError as err:
        return render_template('html/err.html', err=err.message)

    return render_template(
        'html/bus_ticket.html',
        bus_data=ticket_data[0],
        ticket=ticket_data[1],
        javascript=ticket_data[2]
    )


@school_bus_bp.route('/alipay')
def alipay() -> render_template:
    """
    调起支付宝支付
    :return:
    """
    return render_template('html/alipay.html', trade_no=request.args.get('tradeNo'))


@school_bus_bp.route('/alipay/qrcode')
def alipay_qrcode() -> send_file:
    """
    二维码生成
    :return:
    """
    alipay_url = get_alipay_url(request.args.get('tradeNo'))
    return send_file(get_qrcode(url=alipay_url), mimetype='image/png')
