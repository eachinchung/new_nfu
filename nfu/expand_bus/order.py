from os import getenv

from nfu.common import generate_auth_key
from nfu.expand.token import generate_token
from nfu.expand_bus.network import http_post
from nfu.nfu_error import NFUError


def __get_order_list(list_type: int) -> list:
    """
    获取订单列表
    :param list_type:
    :return:
    """
    url = 'http://nfuedu.zftcloud.com/campusbus_index/order/refresh.html'

    data = {
        'type': list_type,
        'page': 1  # 默认给1，一个账号不可能同时有太多订单
    }

    return http_post(url, data)


def create_order(passenger_ids: str, connect_id: int, schedule_id: int, date: str, take_station: str) -> dict:
    """
    创建车票订单

    支付宝H5开发文档，支付篇：
    https://myjsapi.alipay.com/alipayjsapi/util/pay/tradepay.html

    :param passenger_ids: 乘客id
    :param connect_id: 联系人id
    :param schedule_id: 班车id
    :param date: 日期
    :param take_station: 乘车车站
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

    response = http_post(url, data)

    if not response['code'] == '10000':
        raise NFUError(response['desc'], code=response['code'])

    return {
        'tradeNo': response['trade_no'],
        'outTradeNo': response['out_trade_no'],
        'orderId': response['order_id']
    }


def get_waiting_ride_order(user_id: int) -> list:
    """
    获取待乘车订单
    :param user_id:
    :return:
    """
    response = __get_order_list(0)
    result = []

    for item in response:
        # 生成访问电子车票的token
        token = generate_token({
            'userId': user_id,
            'orderId': item['id']
        }, token_type='TICKET_TOKEN', expires_in=604800)

        # 生成cdn鉴权的 auth_key
        uri = f'/school-bus/ticket/{token}'
        auth_key = generate_auth_key(uri, 604800)

        result.append({
            'id': item['id'],
            'date': item['date'],
            'week': item['week'],
            'startTime': item['start_time'],
            'price': item['price'],
            'startFromName': item['start_from_name'],
            'startToName': item['start_to_name'],
            'ticketUrl': f"{getenv('API_URL')}{uri}?auth_key={auth_key}"
        })

    return result


def get_pending_payment_order() -> list:
    """
    获取待付款的订单
    :return:
    """
    response = __get_order_list(1)
    result = []

    for item in response:
        result.append({
            'id': item['id'],
            'date': item['date'],
            'week': item['week'],
            'startTime': item['start_time'],
            'price': item['price'],
            'startFromName': item['start_from_name'],
            'startToName': item['start_to_name']
        })

    return result
