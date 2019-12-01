from io import BytesIO
from os import getenv
from re import S, findall, search
from urllib.parse import quote

import qrcode

from nfu.expand_bus.network import http_get, http_post
from nfu.nfu_error import NFUError


def get_ticket_data(order_id: int) -> tuple:
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
    :return bus_data: 班车数据，同个订单，统一即可
    :return ticket: 车票数据
    :return javascript: 处理车票的js，动态生成js，实在是太骚了。
    """

    url = 'http://nfuedu.zftcloud.com/campusbus_index/order/ticket.html'
    params = {'order_id': order_id}
    response = http_get(url, params)

    try:
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

    except AttributeError:
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


def return_ticket(order_id: int, ticket_id: int) -> str:
    """
    退票

    :param order_id: 订单id
    :param ticket_id: 车票id
    :return:
    """

    url = 'http://nfuedu.zftcloud.com/campusbus_index/order/refund_ticket.html'

    data = {
        'order_id': order_id,
        'ticket_id': ticket_id
    }

    response = http_post(url, data)

    if response['code'] != '0000':
        raise NFUError(response['desc'])

    return response['desc']


def get_qrcode(url: str) -> BytesIO:
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


def get_alipay_url(trade_no: str) -> str:
    """
    返回唤醒alipay的url
    :param trade_no:
    :return:
    """
    url = f"{getenv('API_URL')}/school-bus/alipay?tradeNo={trade_no}"
    return f"alipays://platformapi/startapp?appId=20000067&url={quote(url, 'utf-8')}"
