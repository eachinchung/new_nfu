from flask import Blueprint, g, jsonify, render_template, request

from nfu.decorators import check_access_token, check_power_school_bus
from nfu.expand.school_bus import get_bus_schedule, get_passenger_data, get_ticket_data, get_ticket_ids, return_ticket

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

    schedule = get_bus_schedule(route_id, date, g.user.bus_session)
    if not schedule[0]:
        return jsonify({'adopt': False, 'message': schedule[1]}), 500

    return jsonify({'adopt': True, 'message': schedule[1]})


@school_bus_bp.route('/passenger/get', methods=['POST'])
@check_access_token
@check_power_school_bus
def get_passenger():
    """
    获取乘车人数据
    :return:
    """
    passenger = get_passenger_data(g.user.bus_session)
    if not passenger[0]:
        return jsonify({'adopt': False, 'message': passenger[1]}), 500

    return jsonify({'adopt': True, 'message': passenger[1]})


@school_bus_bp.route('/ticket_id/get', methods=['POST'])
@check_access_token
@check_power_school_bus
def get_ticket_ids_bp():
    """
    获取车票的id，用于退票
    :return:
    """
    order_id = request.form.get('order_id')
    ticket_ids = get_ticket_ids(order_id, g.user.bus_session)

    if not ticket_ids[0]:
        return jsonify({'adopt': False, 'message': ticket_ids[1]}), 500

    return jsonify({'adopt': True, 'message': ticket_ids[1]})


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

    post = return_ticket(order_id, ticket_id, g.user.bus_session)

    if not post[0]:
        return jsonify({'adopt': False, 'message': post[1]}), 500

    return jsonify({'adopt': True, 'message': post[1]})


@school_bus_bp.route('/ticket/get')
@check_access_token
@check_power_school_bus
def get_ticket():
    """
    获取电子车票
    :return:
    """
    order_id = request.args.get('order_id')
    ticket_data = get_ticket_data(order_id, g.user.bus_session)

    if not ticket_data[0]:
        return ticket_data[1], 500

    return render_template(
        'html/bus_ticket.html',
        bus_data=ticket_data[1],
        ticket=ticket_data[2],
        javascript=ticket_data[3]
    )