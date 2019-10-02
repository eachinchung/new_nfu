from json import loads, decoder
from re import search

from requests import session


def get_bus_schedule(route_id: int, date: list, bus_session: str) -> tuple:
    """
    若日期在车票预售期内，获取班车时刻表。

    学校的校车系统，并没有做前后端分离，每天的班车数据都会在页面直接返回。
    我们用正则抓取即可，同时只要提交日期就可以查看当天车票，并无太多限制。

    - 字段说明
        - route_id 路线id：南苑 -> 河堤公园：21，
                          河堤公园 -> 南苑：22，
                          南苑 -> 中大南校区：13，
                          中大南校区 -> 南苑：14

        - time     乘车日期

    :param route_id: 校车路线
    :param date: 乘车日期
    :param bus_session: 校车系统的 session
    :return: 0.是否成功获取数据，1.数据
    """

    url = 'http://nfuedu.zftcloud.com/campusbus_index/ticket/show_schedule.html'
    http_session = session()
    params = {
        'route_id': route_id,
        'time': date
    }
    headers = {'Cookie': bus_session}

    try:
        response = http_session.get(url, params=params, headers=headers)
        data = loads(search(r'var msg = .+', response.text).group()[10:-1])
    except (OSError, AttributeError, decoder.JSONDecodeError):
        return False, '学校车票系统错误，请稍后再试'
    else:
        return True, data


def get_bus_passenger(bus_session: str) -> tuple:
    """
    获取乘车人数据
    同样，数据都会在页面直接返回。
    :param bus_session: 校车系统的 session
    :return: 0.是否成功获取数据，1.数据
    """
    url = 'http://nfuedu.zftcloud.com/campusbus_index/my/passenger_puls.html'
    headers = {'Cookie': bus_session}
    http_session = session()

    try:
        response = http_session.get(url, headers=headers)
        passenger = loads(search(r'var passenger = .+', response.text).group()[16:-1])
    except (OSError, AttributeError, decoder.JSONDecodeError):
        return False, '学校车票系统错误，请稍后再试'
    else:
        return True, passenger
