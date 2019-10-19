from flask import Blueprint, g, jsonify

from nfu.achievement_expand import db_get, db_init, db_update
from nfu.decorators import check_access_token, get_config
from nfu.models import Achievement, TotalAchievements
from nfu.total_achievement_expand import db_init_total, db_update_total

achievement_bp = Blueprint('achievement', __name__)


@achievement_bp.route('/get', methods=['POST'])
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

    achievement = db_init(g.user.id, school_year, semester)
    if achievement[0]:
        return jsonify({'adopt': True, 'message': achievement[1]})

    return jsonify({'adopt': False, 'message': achievement[1]}), 500


@achievement_bp.route('/update', methods=['POST'])
@check_access_token
@get_config
def update(school_year, semester):
    """
    更新成绩单
    :param school_year:
    :param semester:
    :return:
    """

    achievement_update = db_update(g.user.id, school_year, semester)
    if achievement_update[0]:
        return jsonify({'adopt': True, 'message': achievement_update[1]})

    return jsonify({'adopt': False, 'message': achievement_update[1]}), 500


@achievement_bp.route('/total/get', methods=['POST'])
@check_access_token
def get_total():
    """
    获取总体成绩信息
    :return:
    """

    achievement_db = TotalAchievements.query.get(g.user.id)
    if achievement_db:
        return jsonify({'adopt': True, 'message': achievement_db.get_dict()})

    total_achievement = db_init_total(g.user.id)
    if total_achievement[0]:
        return jsonify({'adopt': True, 'message': total_achievement[1]})

    return jsonify({'adopt': False, 'message': total_achievement[1]}), 500


@achievement_bp.route('/total/update', methods=['POST'])
@check_access_token
def update_total():
    """
    更新总体成绩信息
    :return:
    """
    achievement_update = db_update_total(g.user.id)
    if achievement_update[0]:
        return jsonify({'adopt': True, 'message': achievement_update[1]})

    return jsonify({'adopt': False, 'message': achievement_update[1]}), 500
