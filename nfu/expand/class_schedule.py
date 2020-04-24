from hashlib import md5
from json import dumps, loads

from nfu.expand.nfu import get_class_schedule, get_jw_token
from nfu.extensions import db
from nfu.models import ClassSchedule


def db_init(user_id: int, jw_pwd: str, school_year: int, semester: int, redis) -> list:
    """
    数据库没有课表数据时，调用此函数写入数据
    :param jw_pwd:
    :param redis:
    :param user_id:
    :param school_year:
    :param semester:
    :return:
    """

    token = get_jw_token(user_id, jw_pwd)
    class_schedule_api = get_class_schedule(token, school_year, semester)

    version = md5(dumps(class_schedule_api).encode(encoding='UTF-8')).hexdigest()
    redis.set(f'class-schedule-version-{user_id}', version)

    class_schedule = __db_input(user_id, class_schedule_api, school_year, semester)
    redis.set(f'class-schedule-{user_id}', dumps(class_schedule))
    return class_schedule


def db_update(user_id: int, jw_pwd: str, school_year: int, semester: int, redis) -> list:
    """
    更新数据库中的课表数据
    :param jw_pwd:
    :param redis:
    :param user_id:
    :param school_year:
    :param semester:
    :return:
    """

    token = get_jw_token(user_id, jw_pwd)

    # 先尝试连接教务系统，看是否能获取课程数据
    class_schedule_api = get_class_schedule(token, school_year, semester)
    version = md5(dumps(class_schedule_api).encode(encoding='UTF-8')).hexdigest()

    class_schedule_version = redis.get(f'class-schedule-version-{user_id}')

    # 若检测到数据有更新，则写入mysql
    if class_schedule_version is None or class_schedule_version.decode('utf-8') != version:

        class_schedule_db = ClassSchedule.query.filter_by(
            user_id=user_id,
            school_year=school_year,
            semester=semester
        ).all()

        for course in class_schedule_db:
            db.session.delete(course)

        db.session.commit()

        # 写入缓存
        class_schedule = __db_input(user_id, class_schedule_api, school_year, semester)
        redis.set(f'class-schedule-version-{user_id}', version)
        redis.set(f'class-schedule-{user_id}', dumps(class_schedule))

    else:  # 否则直接读取缓存数据
        class_schedule = redis.get(f'class-schedule-{user_id}').decode('utf-8')
        class_schedule = loads(class_schedule)

    return class_schedule


def __db_input(user_id, class_schedule_list: list, school_year: int, semester: int) -> list:
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
                subdivision_type=course['subdivision_type'],
                course_name=course['course_name'],
                course_id=course['course_id'],
                credit=float(course['credit']),
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
            'courseId': course['course_id'],
            'subdivisionType': course['subdivision_type'],
            'courseName': course['course_name'],
            'credit': float(course['credit']),
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
