from flask import Blueprint, g, jsonify

from nfu.common import check_access_token, get_config
from nfu.expand.achievement import db_get, db_init, db_update
from nfu.expand.total_achievement import db_init_total, db_update_total
from nfu.models import Achievement, TotalAchievements
from nfu.NFUError import NFUError

achievement_bp = Blueprint('achievement', __name__)


@achievement_bp.route('/get')
@check_access_token
@get_config
def get(school_year, semester):
    """
    获取成绩单
    :param school_year:
    :param semester:
    :return:
    """

    achievement_db = Achievement.query.filter_by(user_id=g.user.id).all()
    if achievement_db:
        return jsonify({'adopt': True, 'message': db_get(achievement_db, g.user.id, school_year, semester)})

    try:
        return jsonify({'adopt': True, 'message': db_init(g.user.id, school_year, semester)})
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})


@achievement_bp.route('/update')
@check_access_token
@get_config
def update(school_year, semester):
    """
    更新成绩单
    :param school_year:
    :param semester:
    :return:
    """
    try:
        achievement_update = db_update(g.user.id, school_year, semester)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})

    return jsonify({'adopt': True, 'message': achievement_update})


@achievement_bp.route('/total')
@check_access_token
def get_total():
    """
    获取总体成绩信息
    :return:
    """

    achievement_db = TotalAchievements.query.get(g.user.id)
    if achievement_db:
        return jsonify({'adopt': True, 'message': achievement_db.get_dict()})

    try:
        total_achievement = db_init_total(g.user.id)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})

    return jsonify({'adopt': True, 'message': total_achievement})


@achievement_bp.route('/update/total')
@check_access_token
def update_total():
    """
    更新总体成绩信息
    :return:
    """
    try:
        achievement_update = db_update_total(g.user.id)
    except NFUError as err:
        return jsonify({'adopt': False, 'message': err.message})

    return jsonify({'adopt': True, 'message': achievement_update})
