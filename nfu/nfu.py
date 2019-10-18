from json import decoder, loads, dumps

from requests import session


def get_jw_token(student_id: int, password: str = '') -> tuple:
    """
    登陆教务系统
    :param student_id: 学号，基于教务系统的Bug，登陆时，密码直接提交空字符串就可以了
    :param password: 密码，默认为空字符串
    :return: 一个元组，通常我规定第一个为bool，用来判定是否成功获取数据。
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
        response = http_session.post(url, data=data, timeout=1)
        token = loads(response.text)['msg']
    except (OSError, decoder.JSONDecodeError):
        return False, '教务系统错误，请稍后再试'

    if not token:
        return False, '学号或密码错误!'

    return True, token


def get_student_name(student_id: int, password: str) -> tuple:
    """
    与教务系统校对账号密码，并获取学生姓名

    - 字段说明
        - username 学号
        - password 密码
        - rd 随机数，可以随机，也可以不填，我也不知道来干嘛的

    :param student_id: 学号
    :param password: 教务系统的密码
    :return: 一个元组，通常我规定第一个为bool，用来判定是否成功获取数据。
    :raise OSError: 一般错误为超时，学校系统炸了，与我们无关
    """

    token = get_jw_token(student_id, password)

    if not token:
        return False,token[1]

    url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-getMyself'
    data = {'jwloginToken': token[1]}
    http_session = session()

    try:
        response = http_session.post(url, data=data, timeout=1)
        name = loads(response.text)['msg']['name']
    except (OSError, KeyError):
        return False, '教务系统错误，请稍后再试'

    if not name:
        return False, '没有获取到数据，请稍后再试'

    return True, name


def get_class_schedule(token: str, school_year: int, semester: int) -> tuple:
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
        response = http_session.post(url, data=data, timeout=1)
        course_list = loads(response.text)['msg']
    except (OSError, KeyError, decoder.JSONDecodeError):
        return False, '教务系统错误，请稍后再试'

    # 判断获取的数据是否是列表，如果不是列表，可能教务系统又炸了
    if not isinstance(course_list, list):
        return False, '教务系统错误，请稍后再试'

    for course in course_list:  # 循环所有课程
        for merge in course['kbMergeList']:  # 课程可能有不同上课时间，循环取出

            teacher = []
            for teacher_list in merge['teacherList']:
                teacher.append(teacher_list['xm'])

            course_data.append({
                'course_name': course['name'],
                'course_id': course['pkbdm'],
                'teacher': dumps(teacher),
                'classroom': merge['classroomList'][0]['jsmc'],
                'weekday': merge['xq'],
                'start_node': merge['qsj'],
                'end_node': merge['jsj'],
                'start_week': merge['qsz'],
                'end_week': merge['jsz']
            })

    return True, course_data


def get_achievement_list(token: str, school_year: int, semester: int) -> tuple:
    """
    获取成绩单
    :param token:
    :param school_year:
    :param semester:
    :return:
    """

    course_list = {
        'year': school_year,
        'semester': semester,
        'data': []
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
        response = http_session.post(url, data=data, timeout=1)
    except OSError:
        return False, '教务系统错误，请稍后再试'

    try:
        course = loads(response.text)['msg']
    except (KeyError, decoder.JSONDecodeError):
        return False, '教务系统错误，请稍后再试'

    try:
        course = course['list']
    except KeyError:
        return False, course

    if not course:
        return False, '学校教务系统返回数据为空'

    course_list['data'].append({'year': school_year, 'semester': semester, 'data': course})
    return True, course_list


def get_total_achievement_point(token: str) -> tuple:
    """
    获取学分、成绩的总体情况
    :param token:
    :return:
    """

    url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-getMyself'
    http_session = session()
    data = {'jwloginToken': token}

    try:  # 先获取学生的真实id
        response = http_session.post(url, data=data)
        actual_id = loads(response.text)['msg']['actualId']

    except (OSError, KeyError, decoder.JSONDecodeError):
        return False, '教务系统错误，请稍后再试'

    if not actual_id:
        return False, '没有获取到该学生的真实id'

    url = 'http://ecampus.nfu.edu.cn:2929/jw-amsi/AmsJxbXsZgcj/listXs'
    data = {
        'deleted': False,
        'pageSize': 65535,
        'id': actual_id,
        'jwloginToken': token
    }

    try:
        response = http_session.post(url, data=data)
        data = loads(response.text)['msg']['list'][0]
    except (OSError, KeyError, decoder.JSONDecodeError):
        return False, '教务系统错误，请稍后再试'

    if not data:
        return False, '没有获取到数据，请稍后再试'

    return True, {
        'selected_credit': data['yxxf'],
        'get_credit': data['yhdxf'],
        'average_achievement': data['avg'],
        'average_achievement_point': data['avgJd']
    }
