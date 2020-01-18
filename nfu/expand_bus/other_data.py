from json import decoder, loads
from os import getenv
from re import findall, search

from nfu.expand_bus.network import http_get
from nfu.expand_bus.ticket import get_alipay_url
from nfu.nfu_error import NFUError


def get_bus_schedule(route_id: int, date: list) -> dict:
    """
    若日期在车票预售期内，获取班车时刻表。

    - 字段说明
        - route_id 路线id：南苑 -> 河堤公园：21，
                          河堤公园 -> 南苑：22，
                          南苑 -> 中大南校区：13，
                          中大南校区 -> 南苑：14

        - time     乘车日期

    :param route_id: 校车路线
    :param date: 乘车日期
    :return:
    """

    url = 'http://nfuedu.zftcloud.com/campusbus_index/ticket/show_schedule.html'
    params = {
        'route_id': route_id,
        'time': date
    }
    response = http_get(url, params)

    try:
        data = loads(search(r'var msg = .+', response.text).group()[10:-1])
    except (AttributeError, decoder.JSONDecodeError):
        raise NFUError('学校车票系统错误，请稍后再试')
    else:
        return data


def get_passenger_data() -> list:
    """
    获取乘车人数据
    :return:
    """
    url = 'http://nfuedu.zftcloud.com/campusbus_index/my/passenger_puls.html'
    response = http_get(url)

    try:
        passenger = loads(search(r'var passenger = .+', response.text).group()[16:-1])
    except (AttributeError, decoder.JSONDecodeError):
        raise NFUError('学校车票系统错误，请稍后再试')
    else:
        return passenger


def get_pay_order(order_id: int, ) -> dict:
    """
    获取订单的支付数据
    :param order_id:
    :return:
    """
    url = f'http://nfuedu.zftcloud.com/campusbus_index/order/notpay_order/order_id/{order_id}.html'
    response = http_get(url)

    route, date = get_route(response.text)

    try:
        names = findall(r'<span class="title_name title_w">\D+</span>', response.text)
        phones = findall(r'<span class="title_iphone">\d+</span>', response.text)
        trade_no = search(r'var tradeNo = .+', response.text).group()[15:-2]
        price = search(r'￥<span>\d+</span>', response.text).group()[7:-7]
    except AttributeError:
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
        'alipayQrUrl': f"{getenv('API_URL')}/school-bus-plus/alipay/qrcode?tradeNo={trade_no}"
    }


def get_ticket_ids(order_id: int) -> dict:
    """
    因为一个订单里面可能有多张车票，所以我们爬取一下车票号
    :param order_id: 订单id
    :return:
    """

    url = 'http://nfuedu.zftcloud.com/campusbus_index/order/refund_ticket.html'
    params = {'order_id': order_id}
    response = http_get(url, params)

    route, date = get_route(response.text)

    ticket_list = []

    ticket_data = findall(r'<span class="title_name title_w">.+\n.+\n.+\n.+\n.+', response.text)

    try:
        price = search(r'<span class="fare">\d+</span>', response.text).group()[19:-7]
    except AttributeError:
        raise NFUError('学校车票系统错误，请稍后再试')

    for ticket in ticket_data:

        try:
            name = search(r'w">.+<s', ticket).group()[3:-9]
            phone = search(r'<span class="title_iphone">\d+</span>', ticket).group()[27:-7]

        except AttributeError:
            raise NFUError('学校车票系统错误，请稍后再试')

        try:
            ticket_id = search(r', \d+', ticket).group()[2:]
        except AttributeError:
            ticket_list.append({
                'state': '已退票',
                'name': name,
                'phone': phone
            })
        else:
            ticket_list.append({
                'state': f'{price}¥',
                'name': name,
                'phone': phone,
                'ticketId': ticket_id
            })

    return {
        'route': route,
        'date': date,
        'passengerList': ticket_list
    }


def get_route(response):
    """
    从html中获取路径数据
    :param response:
    :return:
    """
    try:
        route = '{} -> {}'.format(
            search(r'<span class="site_from">.+</span>', response).group()[24:-7],
            search(r'<span class="site_to">.+</span>', response).group()[22:-7]
        )
        date = '{} {}'.format(
            search(r'<span class="time_go">\S+</span>', response).group()[22:-7],
            search(r'<span class="time_day">\S+</span>', response).group()[23:-7]
        )
    except AttributeError:
        raise NFUError('学校车票系统错误，请稍后再试')

    return route, date
