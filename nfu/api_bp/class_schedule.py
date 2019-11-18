from flask import Blueprint, g, jsonify

from nfu.common import check_access_token, get_config
from nfu.expand.class_schedule import db_init, db_update
from nfu.models import ClassSchedule
from nfu.NFUError import NFUError

class_schedule_bp = Blueprint('class_schedule', __name__)


@class_schedule_bp.route('/get')
@check_access_token
@get_config
def get(school_year, semester):
    """
    获取课程表数据
    :param school_year:
    :param semester:
    :return:
    """

    class_schedule = []
    class_schedule_db = ClassSchedule.query.filter_by(
        user_id=g.user.id,
        school_year=school_year,
        semester=semester
    ).all()

    if class_schedule_db:  # 数据库中有缓存课程表

        for course in class_schedule_db:
            class_schedule.append(course.get_dict())

        return jsonify({'code': '1000', 'message': class_schedule})

    # 获取课程表，并写入数据库
    try:
        return jsonify({'code': '1000', 'message': db_init(g.user.id, school_year, semester)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@class_schedule_bp.route('/update')
@check_access_token
@get_config
def update(school_year, semester):
    """
    更新课程表数据
    :param school_year:
    :param semester:
    :return:
    """

    try:
        return jsonify({'code': '1000', 'message': db_update(g.user.id, school_year, semester)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})
