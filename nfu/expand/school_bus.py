from io import BytesIO
from json import decoder, loads
from re import S, findall, search

import qrcode
from requests import session

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
        raise NFUError('学校车票系统错误，请稍后再试')
    else:
        return data


def get_passenger_data(bus_session: str) -> list:
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
        raise NFUError('学校车票系统错误，请稍后再试')
    else:
        return passenger


def create_order(passenger_ids: str, connect_id: int, schedule_id: int, date: str, take_station: str,
                 bus_session: str) -> dict:
    """
    创建车票订单

    若返回成功，我们就成功抢到票票了。此时前往支付宝就可以看到票。
    当然，我们同时返回了订单数据，此数据可以直接唤醒支付宝的支付功能。

    支付成功，校巴系统返回实例：
    {"code": "10000", "msg": "Success", "out_trade_no": "1155720191002201122528248",
    "trade_no": "2019100222001417680577082241", "order_id": "527469"}

    支付宝H5开发文档，支付篇：
    https://myjsapi.alipay.com/alipayjsapi/util/pay/tradepay.html

    校巴订单详情页：http://nfuedu.zftcloud.com/campusbus_index/order/order_detail/id/订单号.html
    校巴电子票页面：http://nfuedu.zftcloud.com/campusbus_index/order/ticket.html?order_id=订单号

    校巴获取订单接口：
        - URL：http://nfuedu.zftcloud.com/campusbus_index/order/refresh.html
        - body：
                type: 标签页 0.待乘车 1.待付款 3.全部
                page: 默认为 1 就好

    :param passenger_ids: 乘客id
    :param connect_id: 联系人id
    :param schedule_id: 班车id
    :param date: 日期
    :param take_station: 乘车车站
    :param bus_session: 校车系统的 session
    :return: 错误信息，或订单数据
    """

    url = 'http://nfuedu.zftcloud.com/campusbus_index/order/create_order.html'
    data = {
        'passenger_ids': passenger_ids,
        'connect_id': connect_id,
        'schedule_id': schedule_id,
        'date': date,
        'take_station': take_station,
        'seat_num': ''  # 此数据为座位号，抢票要什么座位要求，直接为空
    }
    headers = {'Cookie': bus_session}
    http_session = session()

    try:
        response = http_session.post(url, data=data, headers=headers)
        response = loads(response.text)
    except (OSError, decoder.JSONDecodeError):
        raise NFUError('学校车票系统错误，请稍后再试')

    if not response['code'] == '10000':
        raise NFUError(response['desc'], code=response['code'])

    return {
        'trade_no': response['trade_no'],
        'out_trade_no': response['out_trade_no'],
        'order_id': response['order_id']
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
            'road_from': search(r'<span class="road_from">.+', response.text).group()[:-1],
            'road_to': search(r'<span class="road_to">.+', response.text).group()[:-1],
            'year': search(r'<span class="data_y">.+', response.text).group()[:-1],
            'week': search(r'<span class="data_week">.+', response.text).group()[:-1],
            'time': search(r'<span class="data_hm">.+', response.text).group()[:-1],
            'bus_id': search(r'<div class="data_bc">.+', response.text).group()[:-1],
            'take_station': search(r'上车点：.+', response.text).group()[:-5]
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
            'ticket_id': ticket_id[:-1],
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
                'code': 1001,
                'name': name
            })
        else:
            ticket_list.append({
                'code': 1000,
                'name': name,
                'ticket_id': ticket_id
            })

    return ticket_list


def return_ticket(order_id: int, ticket_id: int, bus_session: str) -> str:
    """
    退票

    :param order_id: 订单id
    :param ticket_id: 车票id
    :param bus_session: 校车系统的 session
    :return:
    """

    url = 'http://nfuedu.zftcloud.com/campusbus_index/order/refund_ticket.html'
    http_session = session()
    headers = {'Cookie': bus_session}

    data = {
        'order_id': order_id,
        'ticket_id': ticket_id
    }

    try:
        response = http_session.post(url, data=data, headers=headers)
        response = loads(response.text)
    except (OSError, decoder.JSONDecodeError):
        raise NFUError('学校车票系统错误，请稍后再试')

    return response['desc']


def get_qrcode(url):
    """
    根据传入的url 生成 二维码对象
    :param url:
    :return:
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )

    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    byte_io = BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    return byte_io
