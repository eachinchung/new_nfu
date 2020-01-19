from json import decoder, loads

from requests import post

from nfu.nfu_error import NFUError


def get_jw_token(student_id: int, password: str = '') -> str:
    """
    登陆教务系统
    :param student_id: 学号
    :param password: 密码，默认为空字符串
    :return token:
    """

    url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-login'
    data = {
        'username': student_id,
        'password': password,
        'rd': ''
    }

    try:
        response = post(url, data=data, timeout=10)
        token = loads(response.text)['msg']
    except (OSError, decoder.JSONDecodeError):
        raise NFUError('教务系统登录接口错误，请稍后再试')

    if not token:
        raise NFUError('学号或密码错误!')

    return token


def get_student_name(student_id: int, password: str) -> str:
    """
    与教务系统校对账号密码，并获取学生姓名

    - 字段说明
        - username 学号
        - password 密码
        - rd 随机数，可以随机，也可以不填，我也不知道来干嘛的

    :param student_id: 学号
    :param password: 教务系统的密码
    :return name:
    """

    token = get_jw_token(student_id, password)
    url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-getMyself'
    data = {'jwloginToken': token}

    try:
        response = post(url, data=data, timeout=10)
        name = loads(response.text)['msg']['name']
    except (OSError, KeyError):
        raise NFUError('实名验证错误，请稍后再试')

    if not name:
        raise NFUError('没有获取到数据，请稍后再试')

    return name


def get_class_schedule(token: str, school_year: int, semester: int) -> list:
    """
    向教务系统请求课程表数据

    :param token:
    :param school_year:
    :param semester:
    :return:
    """
    course_data = []
    url = 'http://ecampus.nfu.edu.cn:2929/jw-cssi/CssStudent/r-listJxb'
    data = {
        'xn': school_year,
        'xq': semester,
        'jwloginToken': token
    }

    try:
        response = post(url, data=data, timeout=10)
        course_list = loads(response.text)['msg']
    except (OSError, KeyError, decoder.JSONDecodeError):
        raise NFUError('教务系统课程表接口错误，请稍后再试')

    # 判断获取的数据是否是列表，如果不是列表，可能教务系统又炸了
    if not isinstance(course_list, list):
        raise NFUError('教务系统错误，请稍后再试')

    for course in course_list:  # 循环所有课程
        for merge in course['kbMergeList']:  # 课程可能有不同上课时间，循环取出

            teacher = []
            for teacher_list in merge['teacherList']:
                teacher.append(teacher_list['xm'])

            course_data.append({
                'course_name': course['name'],
                'course_id': course['pkbdm'],
                'credit': float(course['kcxf']),
                'teacher': teacher,
                'classroom': merge['classroomList'][0]['jsmc'],
                'weekday': merge['xq'],
                'start_node': merge['qsj'],
                'end_node': merge['jsj'],
                'start_week': merge['qsz'],
                'end_week': merge['jsz']
            })

    course_data.sort(key=lambda x: x['course_id'])
    return course_data


def get_achievement_list(token: str, school_year: int, semester) -> list:
    """
    获取成绩单
    :param token:
    :param school_year:
    :param semester:
    :return:
    """

    url = 'http://ecampus.nfu.edu.cn:2929/jw-amsi/AmsJxbXsZgcj/r-list'
    data = {
        'deleted': False,
        'pg': 1,
        'pageSize': 50,
        'kkxn': school_year,
        'xnxq': semester,
        'jwloginToken': token
    }

    try:
        response = post(url, data=data, timeout=10)
    except OSError:
        raise NFUError('教务系统成绩接口错误，请稍后再试')

    try:
        course = loads(response.text)['msg']
    except (KeyError, decoder.JSONDecodeError):
        raise NFUError('教务系统错误，请稍后再试')

    try:
        course = course['list']
    except KeyError:
        raise NFUError(course)

    return course


def get_total_achievement_point(token: str) -> dict:
    """
    获取学分、成绩的总体情况
    :param token:
    :return:
    """

    url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-getMyself'
    data = {'jwloginToken': token}

    try:  # 先获取学生的真实id
        response = post(url, data=data, timeout=10)
        actual_id = loads(response.text)['msg']['actualId']

    except (OSError, KeyError, decoder.JSONDecodeError):
        raise NFUError('教务系统绩点接口错误，请稍后再试')

    if not actual_id:
        raise NFUError('没有获取到该学生的真实id')

    url = 'http://ecampus.nfu.edu.cn:2929/jw-amsi/AmsJxbXsZgcj/listXs'
    data = {
        'deleted': False,
        'pageSize': 65535,
        'id': actual_id,
        'jwloginToken': token
    }

    try:
        response = post(url, data=data, timeout=10)
        data = loads(response.text)['msg']['list'][0]
    except (OSError, KeyError, decoder.JSONDecodeError):
        raise NFUError('教务系统绩点接口错误，请稍后再试')

    if not data:
        raise NFUError('没有获取到数据，请稍后再试')

    return {
        'selected_credit': data['yxxf'],
        'get_credit': data['yhdxf'],
        'average_achievement': data['avg'],
        'average_achievement_point': data['avgJd']
    }
