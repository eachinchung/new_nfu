import json

import requests


# 获取宿舍电费
def get_electric(room: int) -> tuple:
    url = 'http://axf.nfu.edu.cn/electric/getData/getReserveAM'
    data = {'roomId': room}
    try:
        session = requests.session()
        response = session.post(url, data=data, timeout=1)
    except OSError:
        return False, '安心付服务器错误'
    else:
        try:
            electric_quantity = json.loads(response.text)
            electric_quantity = electric_quantity['data']['remainPower']
        except KeyError:
            return False, '此宿舍无数据'
        else:
            electric_quantity = round(float(electric_quantity), 2)
            return True, electric_quantity
