from json import dumps

from nfu.expand.nfu import get_class_schedule, get_jw_token
from nfu.extensions import db
from nfu.models import ClassSchedule


def db_init(user_id: int, school_year: int, semester: int):
    """
    数据库没有课表数据时，调用此函数写入数据
    :param user_id:
    :param school_year:
    :param semester:
    :return:
    """

    token = get_jw_token(user_id)
    class_schedule_api = get_class_schedule(token, school_year, semester)
    return __db_input(user_id, class_schedule_api, school_year, semester)


def db_update(user_id: int, school_year: int, semester: int):
    """
    更新数据库中的课表数据
    :param user_id:
    :param school_year:
    :param semester:
    :return:
    """

    token = get_jw_token(user_id)

    # 先尝试连接教务系统，看是否能获取课程数据
    class_schedule_api = get_class_schedule(token, school_year, semester)

    class_schedule_db = ClassSchedule.query.filter_by(
        user_id=user_id,
        school_year=school_year,
        semester=semester
    ).all()

    for course in class_schedule_db:
        db.session.delete(course)

    db.session.commit()
    return __db_input(user_id, class_schedule_api, school_year, semester)


def __db_input(user_id, class_schedule_list: list, school_year: int, semester: int):
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
                user_id=user_id,
                school_year=school_year,
                semester=semester,
                course_name=course['course_name'],
                course_id=course['course_id'],
                teacher=dumps(course['teacher']),
                classroom=course['classroom'],
                weekday=course['weekday'],
                start_node=course['start_node'],
                end_node=course['end_node'],
                start_week=course['start_week'],
                end_week=course['end_week']
            )
        )

        class_schedule.append({
            'courseName': course['course_name'],
            'teacher': course['teacher'],
            'classroom': course['classroom'],
            'weekday': course['weekday'],
            'startNode': course['start_node'],
            'endNode': course['end_node'],
            'startWeek': course['start_week'],
            'endWeek': course['end_week']
        })

    db.session.commit()
    return class_schedule
