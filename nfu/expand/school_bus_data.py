from json import decoder, loads
from os import getenv
from re import S, findall, search

from requests import session

from nfu.expand.school_bus_order import get_alipay_url
from nfu.NFUError import NFUError


def get_bus_schedule(route_id: int, date: list, bus_session: str) -> dict:
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
    :return:
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
        raise NFUError('学校车票系统错误，请稍后再试')
    else:
        return data


def get_passenger_data(bus_session: str) -> list:
    """
    获取乘车人数据
    同样，数据都会在页面直接返回。
    :param bus_session: 校车系统的 session
    :return:
    """
    url = 'http://nfuedu.zftcloud.com/campusbus_index/my/passenger_puls.html'
    headers = {'Cookie': bus_session}
    http_session = session()

    try:
        response = http_session.get(url, headers=headers)
        passenger = loads(search(r'var passenger = .+', response.text).group()[16:-1])
    except (OSError, AttributeError, decoder.JSONDecodeError):
        raise NFUError('学校车票系统错误，请稍后再试')
    else:
        return passenger


def get_pay_order(order_id: int, bus_session: str) -> dict:
    """
    获取未支付订单的数据
    :param order_id:
    :param bus_session:
    :return:
    """
    url = 'http://nfuedu.zftcloud.com/campusbus_index/order/notpay_order/order_id/{}.html'.format(order_id)
    http_session = session()
    headers = {'Cookie': bus_session}

    try:
        response = http_session.get(url, params={'order_id': order_id}, headers=headers)
        route = '{} -> {}'.format(
            search(r'<span class="site_from">.+</span>', response.text).group()[24:-7],
            search(r'<span class="site_to">.+</span>', response.text).group()[22:-7]
        )
        date = '{} {}'.format(
            search(r'<span class="time_go">\S+</span>', response.text).group()[22:-7],
            search(r'<span class="time_day">\S+</span>', response.text).group()[23:-7]
        )
        names = findall(r'<span class="title_name title_w">\D+</span>', response.text)
        phones = findall(r'<span class="title_iphone">\d+</span>', response.text)
        trade_no = search(r'var tradeNo = .+', response.text).group()[15:-2]
        price = search(r'￥<span>\d+</span>', response.text).group()[7:-7]
    except (OSError, AttributeError):
        raise NFUError('学校车票系统错误，请稍后再试')

    # 把乘客信息处理成一个列表
    passengers = []
    for i, name in enumerate(names):
        passengers.append({
            'name': name[33:-7],
            'phone': phones[i][27:-7]
        })

    return {
        'route': route,
        'date': date,
        'passengers': passengers,
        'price': price,
        'alipayUrl': get_alipay_url(trade_no),
        'alipayQrUrl': getenv('API_URL') + '/schoolBus/alipay/qrcode?tradeNo=' + trade_no
    }


def get_ticket_data(order_id: int, bus_session: str) -> tuple:
    """
    获取电子票的数据

    - 字段说明
        road_from       始发车站
        road_to         终点站
        year            乘车年份
        week            乘车星期
        time            发车时间
        bus_id          班车号
        take_station    乘车车站

    :param order_id: 订单id
    :param bus_session: 校车系统的 session
    :return bus_data: 班车数据，同个订单，统一即可
    :return ticket: 车票数据
    :return javascript: 处理车票的js，动态生成js，实在是太骚了。
    """

    url = 'http://nfuedu.zftcloud.com/campusbus_index/order/ticket.html'
    http_session = session()
    headers = {'Cookie': bus_session}

    try:
        response = http_session.get(url, params={'order_id': order_id}, headers=headers)
        bus_data = {
            'roadFrom': search(r'<span class="road_from">.+', response.text).group()[:-1],
            'roadTo': search(r'<span class="road_to">.+', response.text).group()[:-1],
            'year': search(r'<span class="data_y">.+', response.text).group()[:-1],
            'week': search(r'<span class="data_week">.+', response.text).group()[:-1],
            'time': search(r'<span class="data_hm">.+', response.text).group()[:-1],
            'busId': search(r'<div class="data_bc">.+', response.text).group()[:-1],
            'takeStation': search(r'上车点：.+', response.text).group()[:-5]
        }
        javascript = search(r'<script>.+</script>', response.text, S).group()

    except (OSError, AttributeError):
        raise NFUError('学校车票系统错误，请稍后再试')

    ticket_ids = findall(r'<p class="erwei_num">电子票号：.+', response.text)
    passengers = findall(r'<p class="erwei_num erwei_c"..style="text-align: center;text-indent:0.2.+', response.text)
    seats = findall(r'<p class="erwei_num erwei_c" style="text-align: center;text-indent:.5rem;">座.+', response.text)

    ticket = []

    for i, ticket_id in enumerate(ticket_ids):
        ticket.append({
            'ticketId': ticket_id[:-1],
            'passenger': passengers[i][:-1],
            'seat': seats[i][:-1]
        })

    return bus_data, ticket, javascript


def get_ticket_ids(order_id: int, bus_session: str) -> list:
    """
    因为一个订单里面可能有多张车票，所以我们爬取一下车票号

    :param order_id: 订单id
    :param bus_session: 校车系统的 session
    :return:
    """

    url = 'http://nfuedu.zftcloud.com/campusbus_index/order/refund_ticket.html'
    http_session = session()
    headers = {'Cookie': bus_session}

    try:
        response = http_session.get(url, params={'order_id': order_id}, headers=headers)
    except OSError:
        raise NFUError('学校车票系统错误，请稍后再试')

    ticket_list = []
    ticket_data = findall(r'<span class="title_name title_w">.+\n.+\n.+\n.+\n.+', response.text)

    for ticket in ticket_data:

        try:
            name = search(r'w">.+<s', ticket).group()[3:-9]
        except AttributeError:
            raise NFUError('学校车票系统错误，请稍后再试')

        try:
            ticket_id = search(r', \d+', ticket).group()[2:]
        except AttributeError:
            ticket_list.append({
                'code': '1001',
                'name': name
            })
        else:
            ticket_list.append({
                'code': '1000',
                'name': name,
                'ticketId': ticket_id
            })

    return ticket_list
