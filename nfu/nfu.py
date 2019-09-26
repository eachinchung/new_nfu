import json

import requests


# 与教务系统校对账号密码
def get_student_name(student_id: int, password: str) -> tuple:
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


# 登陆教务系统
def get_jw_token(student_id: int) -> tuple:
    # 基于教务系统的Bug，登陆直接提交空字符串就可以了
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

        if not token:
            return False, '不可预知错误，请稍后再试！'

    except (OSError, json.decoder.JSONDecodeError):
        return False, '教务系统错误，请稍后再试'

    else:
        return True, token
