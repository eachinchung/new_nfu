from flask import Blueprint, request, g, jsonify

from nfu.decorators import check_access_token
from nfu.school_bus import get_ticket_schedule

school_bus_bp = Blueprint('school_bus', __name__)


@school_bus_bp.route('/get_schedule', methods=['POST'])
@check_access_token
def get_schedule():
    """
    获取班车时刻表
    :return:
    """

    if not g.user_power['school_bus']:  # 检测是否有校车功能的权限
        return jsonify({'message': '没有访问权限'}), 403

    route_id = request.form.get('route_id')
    date = request.form.get('date')

    schedule = get_ticket_schedule(route_id, date, g.user.bus_session)
    if not schedule[0]:
        return jsonify({'message': schedule[1]}), 403

    return jsonify({
        'message': 'success',
        'schedule': schedule[1],
    })
