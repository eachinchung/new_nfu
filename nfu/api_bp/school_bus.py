from flask import Blueprint, g, jsonify, render_template, request

from nfu.NFUError import NFUError
from nfu.common import check_access_token, check_power_school_bus
from nfu.expand.school_bus import get_bus_schedule, get_passenger_data, get_ticket_data, get_ticket_ids, return_ticket, \
    create_order
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

    route_id = request.form.get('route_id')
    date = request.form.get('date')

    try:
        schedule = get_bus_schedule(route_id, date, g.user.bus_session)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 500

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
        passenger = get_passenger_data(g.user.bus_session)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 500

    return jsonify({'adopt': True, 'message': passenger})


@school_bus_bp.route('/order/create', methods=['POST'])
@check_access_token
@check_power_school_bus
def create_order_bp():
    passenger_ids = request.form.get('passenger_ids')
    connect_id = request.form.get('connect_id')
    schedule_id = request.form.get('schedule_id')
    date = request.form.get('date')
    take_station = request.form.get('take_station')
    bus_session = g.user.bus_session

    try:
        order = create_order(passenger_ids, connect_id, schedule_id, date, take_station, bus_session)
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
        ticket_ids = get_ticket_ids(request.form.get('order_id'), g.user.bus_session)
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
        post = return_ticket(order_id, ticket_id, g.user.bus_session)
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
        ticket_data = get_ticket_data(order_id, user.bus_session)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message}), 500

    return render_template(
        'html/bus_ticket.html',
        bus_data=ticket_data[0],
        ticket=ticket_data[1],
        javascript=ticket_data[2]
    )
