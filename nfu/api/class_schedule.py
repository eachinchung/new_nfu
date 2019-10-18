from flask import Blueprint, g, jsonify

from nfu.class_schedule_expand import db_init, db_update
from nfu.decorators import check_access_token, get_config
from nfu.models import ClassSchedule
from nfu.nfu import get_jw_token

class_schedule_bp = Blueprint('class_schedule', __name__)


@class_schedule_bp.route('/get', methods=['POST'])
@check_access_token
@get_config
def get(school_year, semester):
    """
    获取课程表数据
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

    # 数据库没有缓存时
    # 登陆教务系统，获取token
    token = get_jw_token(g.user.id)
    if not token[0]:
        return jsonify({'adopt': False, 'message': token[1]}), 500

    # 获取课程表，并写入数据库
    class_schedule = db_init(token[1], school_year, semester)
    if not class_schedule[0]:
        return jsonify({'adopt': False, 'message': class_schedule[1]}), 500

    return jsonify({'adopt': True, 'message': class_schedule[1]})


@class_schedule_bp.route('/update', methods=['POST'])
@check_access_token
@get_config
def update(school_year, semester):
    """
    更新课程表数据
    :return:
    """

    token = get_jw_token(g.user.id)
    if not token[0]:
        return jsonify({'adopt': False, 'message': token[1]}), 500

    class_schedule_update = db_update(token[1], school_year, semester)
    if not class_schedule_update[0]:
        return jsonify({'adopt': False, 'message': class_schedule_update[1]}), 500

    return jsonify({'adopt': True, 'message': '课程表更新成功'})
