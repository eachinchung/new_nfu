from json import decoder, loads

from flask import g
from requests import session

from nfu.expand_bus.user_agent import get_user_agent
from nfu.extensions import db
from nfu.nfu_error import NFUError


def __refresh() -> None:
    """
    刷新 车票session
    :return:
    """
    http_session = session()
    http_session.headers = {'user-agent': get_user_agent()}
    url = 'http://nfuedu.zftcloud.com/campusbus_index/ticket_checked/index'
    params = {
        'school_code': 11557,
        'alipay_user_id': g.bus_user.alipay_user_id,
        'idcard': g.bus_user.id_card,
        'avatar': g.bus_user.avatar,
        'phone': '',
        'real_name': g.user.name
    }

    try:  # 发送请求
        http_session.get(url, params=params)
    except OSError:
        raise NFUError('学校车票系统错误，请稍后再试')

    # 把新的session写入MySql
    g.bus_user.bus_session = f"PHPSESSID={http_session.cookies['PHPSESSID']}"
    db.session.add(g.bus_user)
    db.session.commit()


def http_get(url: str, params=None):
    """
    发送 get 请求
    :param url:
    :param params:
    :return:
    """
    http_session = session()
    http_session.headers = {'Cookie': g.bus_user.bus_session, 'user-agent': get_user_agent()}

    try:  # 发送请求
        response = http_session.get(url, params=params, allow_redirects=False)

        if response.status_code != 200 and g.refresh:
            __refresh()

            # 防止递归死循环
            g.refresh = False
            return http_get(url, params)

    except OSError:
        raise NFUError('学校车票系统错误，请稍后再试')

    return response


def http_post(url: str, data: dict):
    """
    发送 post 请求
    :param url:
    :param data:
    :return:
    """
    http_session = session()
    http_session.headers = {'Cookie': g.bus_user.bus_session, 'user-agent': get_user_agent()}

    try:  # 发送请求
        response = http_session.post(url, data=data, allow_redirects=False)
    except OSError:
        raise NFUError('学校车票系统错误，请稍后再试')

    try:  # 处理返回的数据
        response = loads(response.text)
    except decoder.JSONDecodeError:

        if response.status_code == 200:
            raise NFUError('学校车票系统错误，请稍后再试')

        if g.refresh:
            __refresh()
            g.refresh = False
            return http_post(url, data)

    return response
