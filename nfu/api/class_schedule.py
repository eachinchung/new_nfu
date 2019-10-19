from flask import Blueprint, g, jsonify

from nfu.class_schedule_expand import db_init, db_update
from nfu.decorators import check_access_token, get_config
from nfu.models import ClassSchedule

class_schedule_bp = Blueprint('class_schedule', __name__)


@class_schedule_bp.route('/get', methods=['POST'])
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
        return jsonify({'adopt': True, 'message': class_schedule})

    # 获取课程表，并写入数据库
    class_schedule = db_init(g.user.id, school_year, semester)
    if not class_schedule[0]:
        return jsonify({'adopt': False, 'message': class_schedule[1]}), 500

    return jsonify({'adopt': True, 'message': class_schedule[1]})


@class_schedule_bp.route('/update', methods=['POST'])
@check_access_token
@get_config
def update(school_year, semester):
    """
    更新课程表数据
    :param school_year:
    :param semester:
    :return:
    """

    class_schedule_update = db_update(g.user.id, school_year, semester)
    if not class_schedule_update[0]:
        return jsonify({'adopt': False, 'message': class_schedule_update[1]}), 500

    return jsonify({'adopt': True, 'message': class_schedule_update[1]})
