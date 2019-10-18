from flask import g

from nfu.extensions import db
from nfu.models import ClassSchedule
from nfu.nfu import get_class_schedule


def db_init(token: str, school_year: int, semester: int) -> tuple:
    """
    数据库没有课表数据时，调用此函数写入数据
    :param token:
    :param school_year:
    :param semester:
    :return:
    """
    class_schedule_api = get_class_schedule(token, school_year, semester)

    if not class_schedule_api[0]:
        return False, class_schedule_api[1]

    return True, __db_input(class_schedule_api[1], school_year, semester)


def db_update(token: str, school_year: int, semester: int) -> tuple:
    """
    更新数据库中的课表数据
    :param token:
    :param school_year:
    :param semester:
    :return:
    """

    # 先尝试连接教务系统，看是否能获取课程数据
    class_schedule_api = get_class_schedule(token, school_year, semester)
    if not class_schedule_api[0]:
        return False, class_schedule_api[1]

    class_schedule_db = ClassSchedule.query.filter_by(
        user_id=g.user.id,
        school_year=school_year,
        semester=semester
    ).all()

    for course in class_schedule_db:
        db.session.delete(course)

    db.session.commit()
    return True, __db_input(class_schedule_api[1], school_year, semester)


def __db_input(class_schedule_list: list, school_year: int, semester: int):
    """
    把课程表写入数据库
    :param class_schedule_list:
    :param school_year:
    :param semester:
    :return:
    """
    class_schedule = []
    for course in class_schedule_list:
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
    return class_schedule