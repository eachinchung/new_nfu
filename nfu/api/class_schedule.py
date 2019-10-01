from flask import Blueprint, g

from nfu.decorators import check_access_token
from nfu.models import ClassSchedule

class_schedule_bp = Blueprint('class_schedule', __name__)


@class_schedule_bp.route('/get')
@check_access_token
def get():
    """
    获取课程表数据
    :return:
    """
    class_schedule = ClassSchedule.query.filter_by(user_id=g.user.id).all()

    if not class_schedule:
        return 'None'
