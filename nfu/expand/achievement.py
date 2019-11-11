from nfu.expand.nfu import get_achievement_list, get_jw_token
from nfu.extensions import db
from nfu.models import Achievement


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


def db_init(user_id: int, school_year_now: int, semester_now: int) -> dict:
    """
    从教务系统获取成绩单，并写入数据库
    :param user_id:
    :param school_year_now:
    :param semester_now:
    :return:
    """
    data = __get(user_id, school_year_now, semester_now)

    # 接下来把数据写入数据库
    for year in data:
        for semester in data[year]:
            __db_input(
                user_id,
                data[year][semester],
                year,
                semester
            )

    return data


def db_update(user_id: int, school_year_now: int, semester_now: int) -> dict:
    """
    更新成绩单
    :param user_id:
    :param school_year_now:
    :param semester_now:
    :return:
    """
    data = __get(user_id, school_year_now, semester_now)

    # 从数据库删除已有的记录
    achievement_db = Achievement.query.filter_by(user_id=user_id).all()

    for course in achievement_db:
        db.session.delete(course)

    db.session.commit()

    # 接下来把数据写入数据库
    for year in data:
        for semester in data[year]:
            __db_input(
                user_id,
                data[year][semester],
                year,
                semester
            )

    return data


def __get(user_id: int, school_year_now: int, semester_now: int) -> dict:
    """
    向教务系统请求数据，
    :param user_id:
    :param school_year_now:
    :param semester_now:
    :return:
    """

    token = get_jw_token(user_id)

    school_year_list = __get_school_year_list(user_id, school_year_now, semester_now)

    for school_year in school_year_list:
        for semester in school_year_list[school_year]:
            # 向教务系统请求数据
            achievement_list = get_achievement_list(token, school_year, semester)
            # 此数据，为接口返回的数据
            school_year_list[school_year][semester] = __data_processing(achievement_list['achievement_list'])

    return school_year_list


def __get_school_year_list(user_id: int, school_year_now: int, semester_now: int) -> dict:
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


def __db_input(user_id: int, achievement_list: list, school_year: int, semester: int) -> None:
    """
    往数据库写入数据
    :param user_id:
    :param achievement_list:
    :param school_year:
    :param semester:
    :return:
    """
    for course in achievement_list:
        achievement_db = Achievement(
            user_id=user_id,
            school_year=school_year,
            semester=semester,
            course_type=course['course_type'],
            course_name=course['course_name'],
            course_id=course['course_id'],
            credit=course['credit'],
            achievement_point=course['achievement_point'],
            final_achievements=course['final_achievements'],
            total_achievements=course['total_achievements'],
            midterm_achievements=course['midterm_achievements'],
            practice_achievements=course['practice_achievements'],
            peacetime_achievements=course['peacetime_achievements']
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

    db.session.commit()


def __data_processing(achievement_list: list) -> list:
    """
    处理爬取下来的数据
    :param achievement_list:
    :return:
    """
    achievement = []

    for course in achievement_list:

        # 判断该学生是否重考
        try:
            resit_exam_achievement_point = course['ckcj']
        except KeyError:
            resit_exam = False
            resit_exam_achievement_point = None
        else:
            resit_exam = True

        achievement.append({
            'course_type': course['kcxz'],
            'course_name': course['yjkcmc'],
            'course_id': course['pkbdm'],
            'resit_exam': resit_exam,
            'credit': course['kcxf'],
            'achievement_point': course['jdVal'],
            'final_achievements': course['qmcj'],
            'total_achievements': course['zpcj'],
            'midterm_achievements': course['qzcj'],
            'practice_achievements': course['sjcj'],
            'peacetime_achievements': course['pscj'],
            'resit_exam_achievement_point': resit_exam_achievement_point
        })

    return achievement
