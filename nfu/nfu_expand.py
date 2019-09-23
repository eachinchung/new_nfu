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
        response = post_session.post(url, data=data)
        token = json.loads(response.text)['msg']

        if not token:
            return False, '学号或密码错误!'

    except (OSError, json.decoder.JSONDecodeError):
        return False, '教务系统错误，请稍后再试'

    else:
        url = 'http://ecampus.nfu.edu.cn:2929/jw-privilegei/User/r-getMyself'
        data = {'jwloginToken': token}

        try:
            response = post_session.post(url, data=data)
            name = json.loads(response.text)['msg']['name']

            if not name:
                return False, '教务系统错误，请稍后再试'

            return True, name

        except (OSError, KeyError):
            return False, '教务系统错误，请稍后再试'
