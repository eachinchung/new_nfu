from os import getenv

from flask import Blueprint, g, jsonify
from redis import Redis

from nfu.common import check_access_token, get_school_config
from nfu.expand.class_schedule import db_init, db_update
from nfu.models import ClassSchedule
from nfu.nfu_error import NFUError

class_schedule_bp = Blueprint('class_schedule', __name__)


@class_schedule_bp.route('/get')
@check_access_token
@get_school_config
def get():
    """
    获取课程表数据
    :return:
    """

    class_schedule = []
    class_schedule_db = ClassSchedule.query.filter_by(
        user_id=g.user.id,
        school_year=g.school_config['schoolYear'],
        semester=g.school_config['semester']
    ).all()

    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)

    if class_schedule_db:  # 数据库中有缓存课程表

        for course in class_schedule_db:
            class_schedule.append(course.get_dict())

        return jsonify({
            'code': '1000',
            'message': class_schedule,
            'version': r.get(f'class-schedule-version-{g.user.id}').decode('utf-8')
        })

    # 获取课程表，并写入数据库
    try:
        return jsonify({
            'code': '1000',
            'message': db_init(g.user.id, g.school_config['schoolYear'], g.school_config['semester'], r),
            'version': r.get(f'class-schedule-version-{g.user.id}').decode('utf-8')
        })
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@class_schedule_bp.route('/update')
@check_access_token
@get_school_config
def update():
    """
    更新课程表数据
    :return:
    """

    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)

    try:
        return jsonify({
            'code': '1000',
            'message': db_update(g.user.id, g.school_config['schoolYear'], g.school_config['semester'], r),
            'version': r.get(f'class-schedule-version-{g.user.id}').decode('utf-8')
        })
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@class_schedule_bp.route('/version')
@check_access_token
def version():
    """
    获取缓存的版本号
    :return:
    """
    r = Redis(host='localhost', password=getenv('REDIS_PASSWORD'), port=6379)
    class_schedule_version = r.get(f'class-schedule-version-{g.user.id}')

    if class_schedule_version is None:
        class_schedule_version = 'update'
    else:
        class_schedule_version = class_schedule_version.decode('utf-8')

    return jsonify({
        'code': '1000',
        'version': class_schedule_version
    })


@class_schedule_bp.route('/config')
@check_access_token
@get_school_config
def school_config():
    """
    获取学年配置
    """
    return jsonify({'code': '1000', 'message': g.school_config})
