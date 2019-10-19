from flask import Blueprint, g, jsonify

from nfu.achievement_expand import db_get, db_init, db_update
from nfu.decorators import check_access_token, get_config
from nfu.models import Achievement

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
    if not achievement_update[0]:
        return jsonify({'adopt': False, 'message': achievement_update[1]}), 500

    return jsonify({'adopt': True, 'message': '课程表更新成功'})
