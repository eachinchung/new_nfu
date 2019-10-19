from nfu.extensions import db
from nfu.models import Achievement
from nfu.nfu import get_achievement_list, get_jw_token


def db_get(achievement_db, user_id: int, school_year_now: int, semester_now: int) -> dict:
    """
    从数据库获取成绩单
    :param achievement_db:
    :param user_id:
    :param school_year_now:
    :param semester_now:
    :return:
    """
    achievement = __get_school_year_list(user_id, school_year_now, semester_now)
    for achievement_data in achievement_db:
        achievement[achievement_data.school_year][str(achievement_data.semester)].append(achievement_data.get_dict())

    return achievement


def db_init(user_id: int, school_year_now: int, semester_now: int):
    """
    从教务系统获取成绩单，并写入数据库
    :param user_id:
    :param school_year_now:
    :param semester_now:
    :return:
    """
    token = get_jw_token(user_id)
    if not token[0]:
        return False, token[1]

    school_year_list = __get_school_year_list(user_id, school_year_now, semester_now)

    for school_year in school_year_list:
        for semester in school_year_list[school_year]:
            # 向教务系统请求数据
            achievement_list = get_achievement_list(token[1], school_year, semester)
            if not achievement_list[0]:
                return False, achievement_list[1]

            school_year_list[school_year][semester] = __db_input(
                user_id,
                achievement_list[1]['achievement_list'],
                achievement_list[1]['school_year'],
                achievement_list[1]['semester']
            )

    return True, school_year_list


def db_update(user_id: int, school_year_now: int, semester_now: int):
    """
    更新成绩单
    :param user_id:
    :param school_year_now:
    :param semester_now:
    :return:
    """
    token = get_jw_token(user_id)
    if not token[0]:
        return False, token[1]

    achievement_data = []  # 临时存储数据的列表
    school_year_list = __get_school_year_list(user_id, school_year_now, semester_now)

    for school_year in school_year_list:
        for semester in school_year_list[school_year]:
            # 向教务系统请求数据
            achievement_list = get_achievement_list(token[1], school_year, semester)
            if not achievement_list[0]:
                return False, achievement_list[1]

            # 把数据先用列表临时存储起来
            achievement_data.append(achievement_list[1])

    # 从数据库删除已有的记录
    achievement_db = Achievement.query.filter_by(user_id=user_id).all()

    for course in achievement_db:
        db.session.delete(course)

    db.session.commit()

    # 接下来把数据写入数据库
    for datum in achievement_data:
        __db_input(
            user_id,
            datum['achievement_list'],
            datum['school_year'],
            datum['semester']
        )

    return True, '成绩单更新成功'


def __get_school_year_list(user_id: int, school_year_now: int, semester_now: int):
    """
    获取当前所有有成绩的学年
    :param user_id:
    :param school_year_now:
    :param semester_now:
    :return:
    """
    school_year_list = {}
    school_year_first = 2000 + int(user_id / 10000000)

    while school_year_first < school_year_now:
        school_year_list[school_year_first] = {'1': [], '2': []}
        school_year_first += 1

    if semester_now == 2:
        school_year_list[school_year_now] = {'1': []}

    return school_year_list


def __db_input(user_id: int, achievement_list: list, school_year: int, semester: int):
    """
    往数据库写入数据
    :param user_id:
    :param achievement_list:
    :param school_year:
    :param semester:
    :return:
    """
    achievement = []

    for course in achievement_list:
        achievement_db = Achievement(
            user_id=user_id,
            school_year=school_year,
            semester=semester,
            course_type=course['kcxz'],
            course_name=course['yjkcmc'],
            course_id=course['pkbdm'],
            credit=course['kcxf'],
            achievement_point=course['jdVal'],
            final_achievements=course['qmcj'],
            total_achievements=course['zpcj'],
            midterm_achievements=course['qzcj'],
            practice_achievements=course['sjcj'],
            peacetime_achievements=course['pscj']
        )

        # 判断该学生是否重考
        try:
            achievement_db.resit_exam_achievement_point = course['ckcj']
        except KeyError:
            achievement_db.resit_exam = False
            achievement_db.resit_exam_achievement_point = None
        else:
            achievement_db.resit_exam = True

        db.session.add(achievement_db)

        achievement.append({
            'course_type': course['kcxz'],
            'course_name': course['yjkcmc'],
            'resit_exam': achievement_db.resit_exam,
            'credit': course['kcxf'],
            'achievement_point': course['jdVal'],
            'final_achievements': course['qmcj'],
            'total_achievements': course['zpcj'],
            'midterm_achievements': course['qzcj'],
            'practice_achievements': course['sjcj'],
            'peacetime_achievements': course['pscj'],
            'resit_exam_achievement_point': achievement_db.resit_exam_achievement_point
        })

    db.session.commit()
    return achievement
