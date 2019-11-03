from json import loads

from flask import Blueprint, g, jsonify, render_template, request

from nfu.NFUError import NFUError
from nfu.common import check_access_token, check_power_school_bus
from nfu.expand import school_bus
from nfu.expand.token import validate_token
from nfu.models import User

school_bus_bp = Blueprint('school_bus', __name__)


@school_bus_bp.route('/schedule/get', methods=['POST'])
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
        return jsonify({'adopt': False, 'message': '服务器内部错误'}), 500

    try:
        schedule = school_bus.get_bus_schedule(route_id, date, g.user.bus_session)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})

    return jsonify({'adopt': True, 'message': schedule})


@school_bus_bp.route('/passenger/get')
@check_access_token
@check_power_school_bus
def get_passenger():
    """
    获取乘车人数据
    :return:
    """

    try:
        passenger = school_bus.get_passenger_data(g.user.bus_session)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 500

    return jsonify({'adopt': True, 'message': passenger})


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
        connect_id = data['connect_id']
        schedule_id = data['schedule_id']
        date = data['date']
        take_station = data['take_station']
        bus_session = g.user.bus_session
    except ValueError:
        return jsonify({'adopt': False, 'message': '服务器内部错误'}), 500

    try:
        order = school_bus.create_order(passenger_ids, connect_id, schedule_id, date, take_station, bus_session)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message, 'code': err.code}), 500

    return jsonify({'adopt': True, 'message': order})


@school_bus_bp.route('/ticket_id/get', methods=['POST'])
@check_access_token
@check_power_school_bus
def get_ticket_ids_bp():
    """
    获取车票的id，用于退票
    :return:
    """

    try:
        ticket_ids = school_bus.get_ticket_ids(request.form.get('order_id'), g.user.bus_session)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 500
    return jsonify({'adopt': True, 'message': ticket_ids})


@school_bus_bp.route('/ticket/delete', methods=['POST'])
@check_access_token
@check_power_school_bus
def return_ticket_bp():
    """
    退票
    :return:
    """
    order_id = request.form.get('order_id')
    ticket_id = request.form.get('ticket_id')

    try:
        post = school_bus.return_ticket(order_id, ticket_id, g.user.bus_session)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 500

    return jsonify({'adopt': True, 'message': post})


@school_bus_bp.route('/ticket/get')
def get_ticket():
    """
    获取电子车票
    :return:
    """

    try:
        token_data = validate_token(request.args.get('token'))
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 403

    if not token_data['school_bus']:
        return jsonify({'message': '没有访问权限'}), 403

    user = User.query.get(token_data['id'])
    order_id = request.args.get('order_id')

    try:
        ticket_data = school_bus.get_ticket_data(order_id, user.bus_session)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 500

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
    try:
        token_data = validate_token(request.args.get('token'))
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 403

    if not token_data['school_bus']:
        return jsonify({'message': '没有访问权限'}), 403

    trade_no = request.args.get('trade_no')

    return render_template('html/alipay.html', trade_no=trade_no)
