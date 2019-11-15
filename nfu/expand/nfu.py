from json import decoder, loads

from requests import session

from nfu.NFUError import NFUError


def get_jw_token(student_id: int, password: str = '') -> str:
    """
    登陆教务系统
    :param student_id: 学号
    :param password: 密码，默认为空字符串
    :return token:
    :raise OSError: 一般错误为超时，学校系统炸了，与我们无关
    """

    url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-login'
    http_session = session()
    data = {
        'username': student_id,
        'password': password,
        'rd': ''
    }

    try:
        response = http_session.post(url, data=data, timeout=5)
        token = loads(response.text)['msg']
    except (OSError, decoder.JSONDecodeError):
        raise NFUError('教务系统错误，请稍后再试')

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
    :raise OSError: 一般错误为超时，学校系统炸了，与我们无关
    """

    token = get_jw_token(student_id, password)
    url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-getMyself'
    data = {'jwloginToken': token}
    http_session = session()

    try:
        response = http_session.post(url, data=data, timeout=5)
        name = loads(response.text)['msg']['name']
    except (OSError, KeyError):
        raise NFUError('教务系统错误，请稍后再试')

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
    http_session = session()
    data = {
        'xn': school_year,
        'xq': semester,
        'jwloginToken': token
    }

    try:
        response = http_session.post(url, data=data, timeout=5)
        course_list = loads(response.text)['msg']
    except (OSError, KeyError, decoder.JSONDecodeError):
        raise NFUError('教务系统错误，请稍后再试')

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
                'teacher': teacher,
                'classroom': merge['classroomList'][0]['jsmc'],
                'weekday': merge['xq'],
                'start_node': merge['qsj'],
                'end_node': merge['jsj'],
                'start_week': merge['qsz'],
                'end_week': merge['jsz']
            })

    return course_data


def get_achievement_list(token: str, school_year: int, semester) -> dict:
    """
    获取成绩单
    :param token:
    :param school_year:
    :param semester:
    :return:
    """

    course_list = {
        'school_year': school_year,
        'semester': semester
    }

    url = 'http://ecampus.nfu.edu.cn:2929/jw-amsi/AmsJxbXsZgcj/r-list'
    http_session = session()
    data = {
        'deleted': False,
        'pg': 1,
        'pageSize': 20,
        'kkxn': school_year,
        'xnxq': semester,
        'jwloginToken': token
    }

    try:
        response = http_session.post(url, data=data, timeout=5)
    except OSError:
        raise NFUError('教务系统错误，请稍后再试')

    try:
        course = loads(response.text)['msg']
    except (KeyError, decoder.JSONDecodeError):
        raise NFUError('教务系统错误，请稍后再试')

    try:
        course = course['list']
    except KeyError:
        raise NFUError(course)

    if not course:
        raise NFUError('学校教务系统返回数据为空')

    course_list['achievement_list'] = course
    return course_list


def get_total_achievement_point(token: str) -> dict:
    """
    获取学分、成绩的总体情况
    :param token:
    :return:
    """

    url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-getMyself'
    http_session = session()
    data = {'jwloginToken': token}

    try:  # 先获取学生的真实id
        response = http_session.post(url, data=data, timeout=5)
        actual_id = loads(response.text)['msg']['actualId']

    except (OSError, KeyError, decoder.JSONDecodeError):
        raise NFUError('教务系统错误，请稍后再试')

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
        response = http_session.post(url, data=data, timeout=5)
        data = loads(response.text)['msg']['list'][0]
    except (OSError, KeyError, decoder.JSONDecodeError):
        raise NFUError('教务系统错误，请稍后再试')

    if not data:
        raise NFUError('没有获取到数据，请稍后再试')

    return {
        'selected_credit': data['yxxf'],
        'get_credit': data['yhdxf'],
        'average_achievement': data['avg'],
        'average_achievement_point': data['avgJd']
    }
