from flask import Blueprint, g, jsonify

from nfu.decorators import check_access_token
from nfu.extensions import db
from nfu.models import ClassSchedule
from nfu.nfu import get_class_schedule, get_jw_token

class_schedule_bp = Blueprint('class_schedule', __name__)


@class_schedule_bp.route('/get', methods=['POST'])
@check_access_token
def get():
    """
    获取课程表数据
    :return:
    """

    school_year = 2019
    semester = 1

    class_schedule = []
    class_schedule_db = ClassSchedule.query.filter_by(
        user_id=g.user.id,
        school_year=school_year,
        semester=semester
    ).all()

    if not class_schedule_db:
        # 登陆教务系统，获取token
        token = get_jw_token(g.user.id)

        if not token[0]:
            return jsonify({'adopt': False, 'message': token[1]}), 500

        class_schedule_api = get_class_schedule(token[1], school_year, semester)

        if not class_schedule_api[0]:
            return jsonify({'adopt': False, 'message': class_schedule_api[1]}), 500

        for course in class_schedule_api[1]:
            db.session.add(
                ClassSchedule(
                    user_id=g.user.id,
                    school_year=school_year,
                    semester=semester,
                    course_name=course['course_name'],
                    course_id=course['course_id'],
                    teacher=course['teacher'],
                    classroom=course['classroom'],
                    weekday=course['weekday'],
                    start_node=course['start_node'],
                    end_node=course['end_node'],
                    start_week=course['start_week'],
                    end_week=course['end_week']
                )
            )

            class_schedule.append({
                'course_name': course['course_name'],
                'teacher': course['teacher'],
                'classroom': course['classroom'],
                'weekday': course['weekday'],
                'start_node': course['start_node'],
                'end_node': course['end_node'],
                'start_week': course['start_week'],
                'end_week': course['end_week']
            })

        db.session.commit()

    else:
        for course in class_schedule_db:
            class_schedule.append(course.get_dict())

    return jsonify({'adopt': True, 'message': class_schedule})
