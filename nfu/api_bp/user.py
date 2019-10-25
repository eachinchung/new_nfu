from flask import Blueprint, jsonify, g

from nfu.common import check_access_token
from nfu.models import Dormitory

user_bp = Blueprint('user', __name__)


@user_bp.route('/get')
@check_access_token
def email():
    dormitory = Dormitory.query.get(g.user.room_id)
    return jsonify({
        'id': g.user.id,
        'name': g.user.name,
        'email': g.user.email,
        'dormitory': dormitory.building + ' ' + dormitory.floor + ' ' + str(dormitory.room)
    })
