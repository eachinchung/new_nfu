from flask import Blueprint, g, jsonify

from nfu.common import check_access_token, get_school_config
from nfu.expand.achievement import db_get, db_init, db_update
from nfu.expand.total_achievement import db_init_total, db_update_total
from nfu.models import Achievement, TotalAchievements
from nfu.nfu_error import NFUError

achievement_bp = Blueprint('achievement', __name__)


@achievement_bp.route('/get')
@check_access_token
@get_school_config
def get():
    """
    获取成绩单
    :return:
    """

    achievement_db = Achievement.query.filter_by(user_id=g.user.id).all()

    # 数据库存在成绩数据
    if achievement_db:
        return jsonify({
            'code': '1000',
            'message': db_get(achievement_db)
        })

    try:
        return jsonify({
            'code': '1000',
            'message': db_init(g.user.id, g.school_config['schoolYear'], g.school_config['semester'])
        })
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@achievement_bp.route('/update')
@check_access_token
@get_school_config
def update():
    """
    更新成绩单
    :return:
    """
    try:
        return jsonify({
            'code': '1000',
            'message': db_update(g.user.id, g.school_config['schoolYear'], g.school_config['semester'])
        })
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@achievement_bp.route('/total')
@check_access_token
def get_total():
    """
    获取总体成绩信息
    :return:
    """

    achievement_db = TotalAchievements.query.get(g.user.id)

    # 数据库存在数据
    if achievement_db:
        return jsonify({'code': '1000', 'message': achievement_db.get_dict()})

    try:
        return jsonify({'code': '1000', 'message': db_init_total(g.user.id)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})


@achievement_bp.route('/update/total')
@check_access_token
def update_total():
    """
    更新总体成绩信息
    :return:
    """
    try:
        return jsonify({'code': '1000', 'message': db_update_total(g.user.id)})
    except NFUError as err:
        return jsonify({'code': err.code, 'message': err.message})
