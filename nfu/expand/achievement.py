from nfu.expand.nfu import get_achievement_list, get_jw_token
from nfu.extensions import db
from nfu.models import Achievement


def db_get(achievement_db) -> list:
    """
    从数据库获取成绩单
    :param achievement_db:
    :return:
    """
    achievement = []
    for achievement_data in achievement_db:
        achievement.append(achievement_data.get_dict())

    return achievement


def db_init(user_id: int, school_year_now: int, semester_now: int) -> list:
    """
    从教务系统获取成绩单，并写入数据库
    :param user_id:
    :param school_year_now:
    :param semester_now:
    :return:
    """
    data = __get(user_id, school_year_now, semester_now)

    # 接下来把数据写入数据库
    __db_input(user_id, data)

    return data


def db_update(user_id: int, school_year_now: int, semester_now: int) -> list:
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

    # 提交删除请求
    db.session.commit()

    # 接下来把数据写入数据库
    __db_input(user_id, data)

    return data


def __get(user_id: int, school_year_now: int, semester_now: int) -> list:
    """
    向教务系统请求数据，
    :param user_id:
    :param school_year_now:
    :param semester_now:
    :return:
    """

    token = get_jw_token(user_id)

    achievement_list = []
    school_year_list = __get_school_year_list(user_id, school_year_now, semester_now)

    for item in school_year_list:
        # 向教务系统请求数据
        achievement_data = get_achievement_list(token, item[0], item[1])

        # 判断返回的数据是否为空
        if not achievement_data:
            continue

        # 此数据，为接口返回的数据
        achievement_list.extend(__data_processing(achievement_data, item[0], item[1]))

    return achievement_list


def __get_school_year_list(user_id: int, school_year_now: int, semester_now: int) -> list:
    """
    获取当前所有有成绩的学年
    :param user_id:
    :param school_year_now:
    :param semester_now:
    :return:
    """
    school_year_list = []
    school_year_first = int(f'20{str(user_id)[:2]}')

    while school_year_first < school_year_now:
        school_year_list.append((school_year_first, 1))
        school_year_list.append((school_year_first, 2))
        school_year_first += 1

    if semester_now == 1:
        school_year_list.append((school_year_now, 1))
    else:
        school_year_list.append((school_year_now, 1))
        school_year_list.append((school_year_now, 2))

    return school_year_list


def __db_input(user_id: int, achievement_list: list) -> None:
    """
    往数据库写入数据
    :param user_id:
    :param achievement_list:
    :return:
    """
    for course in achievement_list:
        achievement_db = Achievement(
            user_id=user_id,
            school_year=course['schoolYear'],
            semester=course['semester'],
            course_type=course['courseType'],
            subdivision_type=course['subdivisionType'],
            course_name=course['courseName'],
            course_id=course['courseId'],
            credit=course['credit'],
            resit_exam=course['resitExam'],
            achievement_point=course['achievementPoint'],
            final_achievements=course['finalAchievements'],
            total_achievements=course['totalAchievements'],
            midterm_achievements=course['midtermAchievements'],
            practice_achievements=course['practiceAchievements'],
            peacetime_achievements=course['peacetimeAchievements'],
            resit_exam_achievement_point=course['resitExamAchievementPoint']
        )

        db.session.add(achievement_db)

    db.session.commit()


def __data_processing(achievement_data: list, school_year: int, semester: int) -> list:
    """
    处理爬取下来的数据
    :param achievement_data:
    :return:
    """
    achievement = []

    for course in achievement_data:

        # 判断该学生是否重考
        try:
            resit_exam_achievement_point = float(course['ckcj'])
        except KeyError:
            resit_exam = False
            resit_exam_achievement_point = None
        else:
            resit_exam = True

        achievement.append({
            'schoolYear': school_year,
            'semester': semester,
            'courseType': course['l2kcxz'],
            'subdivisionType': course['kcxz'],
            'courseName': course['yjkcmc'],
            'courseId': course['pkbdm'],
            'resitExam': resit_exam,
            'credit': float(course['kcxf']),
            'achievementPoint': float(course['jdVal']),
            'finalAchievements': float(course['qmcj']),
            'totalAchievements': float(course['zpcj']),
            'midtermAchievements': float(course['qzcj']),
            'practiceAchievements': float(course['sjcj']),
            'peacetimeAchievements': float(course['pscj']),
            'resitExamAchievementPoint': resit_exam_achievement_point
        })

    return achievement
