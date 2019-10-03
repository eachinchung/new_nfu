from flask import Blueprint, request, g, jsonify, render_template

from nfu.decorators import check_access_token, check_power_school_bus
from nfu.school_bus import get_bus_schedule, get_passenger_data, get_ticket_data

school_bus_bp = Blueprint('school_bus', __name__)


@school_bus_bp.route('/get_schedule', methods=['POST'])
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
        return jsonify({'message': schedule[1]}), 500

    return jsonify({
        'message': 'success',
        'schedule': schedule[1],
    })


@school_bus_bp.route('/passenger/get')
@check_access_token
@check_power_school_bus
def get_passenger():
    """
    获取乘车人数据
    :return:
    """
    passenger = get_passenger_data(g.user.bus_session)
    if not passenger[0]:
        return jsonify({'message': passenger[1]}), 500

    return jsonify({
        'message': 'success',
        'passenger': passenger[1],
    })


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
        return jsonify({'message': ticket_data[1]}), 500

    return render_template('html/bus_ticket_cdn.html', bus_data=ticket_data[1], ticket=ticket_data[2],
                           javascript=ticket_data[3])
